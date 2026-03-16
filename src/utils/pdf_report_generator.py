"""PDF Report Generator for Market Intelligence (SOLID principles)."""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
        Image,
    )
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.logging import get_logger

logger = get_logger(__name__)


class MarketIntelligencePDFGenerator:
    """
    Generates PDF reports for Market Intelligence analysis.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles PDF generation
    - Open/Closed: Can be extended with new sections
    """

    def __init__(self):
        """Initialize PDF generator."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab not available. Install with: pip install reportlab"
            )

        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f77b4"),
                spaceAfter=30,
                alignment=1,  # Center
            )
        )

        # Section header
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=12,
                spaceBefore=20,
            )
        )

        # Country header
        self.styles.add(
            ParagraphStyle(
                name="CountryHeader",
                parent=self.styles["Heading2"],
                fontSize=18,
                textColor=colors.HexColor("#34495e"),
                spaceAfter=15,
                spaceBefore=25,
            )
        )

    def _has_data(self, data: Any) -> bool:
        """Check if data exists and is not empty."""
        if data is None:
            return False
        if isinstance(data, dict):
            return len(data) > 0 and not all(
                v is None or v == "" or (isinstance(v, list) and len(v) == 0)
                for v in data.values()
            )
        if isinstance(data, list):
            return len(data) > 0
        if isinstance(data, str):
            return data.strip() != ""
        return True

    def generate_report(
        self,
        result: Dict[str, Any],
        countries: List[str],
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate PDF report from Market Intelligence results.
        
        Args:
            result: Market Intelligence analysis results
            countries: List of analyzed countries
            output_path: Optional path to save PDF (if None, returns bytes)
        
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer if output_path is None else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        story = []

        # Title page
        story.append(Spacer(1, 0.5 * inch))
        story.append(
            Paragraph(
                "Market Intelligence Report",
                self.styles["CustomTitle"],
            )
        )
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
                self.styles["Normal"],
            )
        )
        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Paragraph(
                f"Countries Analyzed: {', '.join(countries)}",
                self.styles["Normal"],
            )
        )
        story.append(PageBreak())

        # Executive Summary
        comparison_summary = result.get("comparison_summary", {})
        if self._has_data(comparison_summary):
            story.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))
            
            summary_data = [
                ["Metric", "Value"],
                ["Countries Analyzed", str(comparison_summary.get("total_countries", 0))],
                ["Total Platforms Found", str(comparison_summary.get("total_platforms", 0))],
                ["Total Opportunities", str(comparison_summary.get("total_opportunities", 0))],
            ]
            
            # Add market sizes if available
            market_sizes = comparison_summary.get("market_sizes", {})
            if market_sizes:
                large_markets = sum(1 for s in market_sizes.values() if s == "large")
                summary_data.append(["Large Markets", str(large_markets)])
            
            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(summary_table)
            story.append(Spacer(1, 0.3 * inch))

        # Results by country
        results_by_country = result.get("results", {})
        
        for country in countries:
            if country not in results_by_country:
                continue
            
            country_result = results_by_country[country]
            
            # Country header
            story.append(Paragraph(f"Country: {country}", self.styles["CountryHeader"]))
            
            # Market Size Analysis
            market_size = country_result.get("market_size", {})
            if self._has_data(market_size):
                story.append(
                    Paragraph("Market Size Analysis", self.styles["SectionHeader"])
                )
                
                market_data = []
                if market_size.get("market_size"):
                    market_data.append(
                        ["Market Size", market_size.get("market_size", "N/A").title()]
                    )
                if market_size.get("active_operators"):
                    market_data.append(
                        ["Active Operators", str(market_size.get("active_operators", 0))]
                    )
                if market_size.get("market_maturity"):
                    market_data.append(
                        ["Market Maturity", market_size.get("market_maturity", "N/A").title()]
                    )
                if market_size.get("growth_potential"):
                    market_data.append(
                        ["Growth Potential", market_size.get("growth_potential", "N/A").title()]
                    )
                if market_size.get("estimated_volume"):
                    market_data.append(
                        ["Estimated Volume", f"${market_size.get('estimated_volume', 0):,}"]
                    )
                
                if market_data:
                    market_table = Table(market_data, colWidths=[2.5 * inch, 2.5 * inch])
                    market_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]
                        )
                    )
                    story.append(market_table)
                    story.append(Spacer(1, 0.2 * inch))
            
            # White Label Platforms
            platforms = country_result.get("platforms", {})
            if self._has_data(platforms) and platforms.get("platforms"):
                story.append(
                    Paragraph("White Label Platforms", self.styles["SectionHeader"])
                )
                
                platforms_list = platforms.get("platforms", [])
                for i, platform in enumerate(platforms_list[:10], 1):  # Limit to 10
                    platform_name = platform.get("name", "Unknown")
                    platform_type = platform.get("type", "white_label").replace("_", " ").title()
                    description = platform.get("description", "")
                    
                    story.append(
                        Paragraph(
                            f"{i}. {platform_name} ({platform_type})",
                            self.styles["Heading3"],
                        )
                    )
                    if description:
                        story.append(
                            Paragraph(description[:300] + ("..." if len(description) > 300 else ""), self.styles["Normal"])
                        )
                    story.append(Spacer(1, 0.1 * inch))
            
            # Growth Opportunities
            opportunities = country_result.get("opportunities", {})
            if self._has_data(opportunities):
                opps_list = opportunities.get("opportunities", [])
                if opps_list:
                    story.append(
                        Paragraph("Growth Opportunities", self.styles["SectionHeader"])
                    )
                    
                    for i, opp in enumerate(opps_list[:10], 1):  # Limit to 10
                        title = opp.get("title", "Opportunity")
                        description = opp.get("description", "")
                        
                        story.append(
                            Paragraph(f"{i}. {title}", self.styles["Heading3"])
                        )
                        if description:
                            story.append(
                                Paragraph(description[:300] + ("..." if len(description) > 300 else ""), self.styles["Normal"])
                            )
                        story.append(Spacer(1, 0.1 * inch))
                
                barriers_list = opportunities.get("entry_barriers", [])
                if barriers_list:
                    story.append(
                        Paragraph("Entry Barriers", self.styles["SectionHeader"])
                    )
                    
                    for i, barrier in enumerate(barriers_list[:10], 1):  # Limit to 10
                        title = barrier.get("title", "Barrier")
                        description = barrier.get("description", "")
                        
                        story.append(
                            Paragraph(f"{i}. {title}", self.styles["Heading3"])
                        )
                        if description:
                            story.append(
                                Paragraph(description[:300] + ("..." if len(description) > 300 else ""), self.styles["Normal"])
                            )
                        story.append(Spacer(1, 0.1 * inch))
            
            # Jurisdiction Analysis
            jurisdiction = country_result.get("jurisdiction", {})
            if self._has_data(jurisdiction) and not jurisdiction.get("error"):
                story.append(
                    Paragraph("Legal & Jurisdiction Analysis", self.styles["SectionHeader"])
                )
                
                regulations = jurisdiction.get("regulations", {})
                if self._has_data(regulations):
                    juris_data = []
                    
                    if regulations.get("legal_status"):
                        juris_data.append(
                            ["Legal Status", regulations.get("legal_status", "N/A").title()]
                        )
                    if regulations.get("licensing_required") is not None:
                        juris_data.append(
                            ["Licensing Required", "Yes" if regulations.get("licensing_required") else "No"]
                        )
                    if regulations.get("regulatory_body"):
                        juris_data.append(
                            ["Regulatory Body", regulations.get("regulatory_body", "N/A")]
                        )
                    
                    if juris_data:
                        juris_table = Table(juris_data, colWidths=[2.5 * inch, 2.5 * inch])
                        juris_table.setStyle(
                            TableStyle(
                                [
                                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                                ]
                            )
                        )
                        story.append(juris_table)
                        story.append(Spacer(1, 0.2 * inch))
                    
                    # Compliance requirements
                    compliance_reqs = regulations.get("compliance_requirements", [])
                    if compliance_reqs:
                        story.append(
                            Paragraph(
                                f"Compliance Requirements: {', '.join(compliance_reqs)}",
                                self.styles["Normal"],
                            )
                        )
                        story.append(Spacer(1, 0.1 * inch))
                
                # Risks and Opportunities
                risks_opps = jurisdiction.get("risks_and_opportunities", {})
                if self._has_data(risks_opps):
                    if risks_opps.get("overall_risk_level"):
                        story.append(
                            Paragraph(
                                f"Overall Risk Level: {risks_opps.get('overall_risk_level', 'N/A').upper()}",
                                self.styles["Normal"],
                            )
                        )
                    if risks_opps.get("overall_opportunity_level"):
                        story.append(
                            Paragraph(
                                f"Opportunity Level: {risks_opps.get('overall_opportunity_level', 'N/A').upper()}",
                                self.styles["Normal"],
                            )
                        )
                    
                    # Recommendations
                    recommendations = risks_opps.get("recommendations", [])
                    if recommendations:
                        story.append(Spacer(1, 0.1 * inch))
                        story.append(
                            Paragraph("Recommendations:", self.styles["Heading3"])
                        )
                        for rec in recommendations:
                            story.append(
                                Paragraph(f"• {rec}", self.styles["Normal"])
                            )
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        if output_path is None:
            buffer.seek(0)
            return buffer.getvalue()
        
        return b""
