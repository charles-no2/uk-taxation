<?xml version="1.0" encoding="UTF-8"?>
<!-- Converts legislation.gov.uk data.xml to readable statutory text. -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:leg="http://www.legislation.gov.uk/namespaces/legislation"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>
  <xsl:param name="source_url"/>
  <xsl:param name="fetched_at"/>
  <xsl:template match="/">
    <xsl:value-of select="/leg:Legislation/*[local-name()='Metadata']/dc:title"/>
    <xsl:text>&#10;Official source: </xsl:text><xsl:value-of select="$source_url"/>
    <xsl:text>&#10;Fetched (UTC): </xsl:text><xsl:value-of select="$fetched_at"/>
    <xsl:text>&#10;&#10;</xsl:text>
    <xsl:apply-templates select="//leg:PrimaryPrelims | //leg:Body | //leg:Schedules"/>
  </xsl:template>
  <xsl:template match="leg:Part | leg:Chapter | leg:Schedule | leg:Crossheading | leg:P1group | leg:Pblock">
    <xsl:text>&#10;&#10;</xsl:text><xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="leg:PrimaryPrelims/leg:Title | leg:Part/leg:Title | leg:Chapter/leg:Title | leg:Schedule/leg:Title | leg:Crossheading/leg:Title | leg:P1group/leg:Title | leg:Pblock/leg:Title">
    <xsl:text>&#10;</xsl:text><xsl:apply-templates/><xsl:text>&#10;</xsl:text>
  </xsl:template>
  <xsl:template match="leg:P1">
    <xsl:text>&#10;&#10;</xsl:text><xsl:apply-templates select="leg:Pnumber"/><xsl:text>. </xsl:text><xsl:apply-templates select="node()[not(self::leg:Pnumber)]"/>
  </xsl:template>
  <xsl:template match="leg:P2">
    <xsl:text>&#10;  (</xsl:text><xsl:apply-templates select="leg:Pnumber"/><xsl:text>) </xsl:text><xsl:apply-templates select="node()[not(self::leg:Pnumber)]"/>
  </xsl:template>
  <xsl:template match="leg:P3">
    <xsl:text>&#10;    (</xsl:text><xsl:apply-templates select="leg:Pnumber"/><xsl:text>) </xsl:text><xsl:apply-templates select="node()[not(self::leg:Pnumber)]"/>
  </xsl:template>
  <xsl:template match="leg:P4 | leg:P5 | leg:P6 | leg:P7 | leg:P8">
    <xsl:text>&#10;      (</xsl:text><xsl:apply-templates select="leg:Pnumber"/><xsl:text>) </xsl:text><xsl:apply-templates select="node()[not(self::leg:Pnumber)]"/>
  </xsl:template>
  <xsl:template match="leg:Pnumber"><xsl:value-of select="normalize-space()"/></xsl:template>
  <xsl:template match="text()"><xsl:value-of select="normalize-space()"/><xsl:text> </xsl:text></xsl:template>
  <xsl:template match="*"><xsl:apply-templates/></xsl:template>
</xsl:stylesheet>
