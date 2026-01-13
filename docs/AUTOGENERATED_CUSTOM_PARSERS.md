# Auto-Generated Custom Parsers

Quick technical points about generic parsers vs. custom document-type specific parsers (e.g., the special "Boston Heart" parser).

## Key Challenges

1. **Maintaining N custom parsers is not scalable**
   - N is an unknown, arbitrarily large number
   - Different format for each lab, hospital, doctor, etc.
   - Manual maintenance would be unsustainable

## Proposed Solution: Auto-Generated Parsers

2. **It might be possible to auto-generate custom parsers**
   - **Recognition phase:** System encounters and recognizes a new, previously unseen document format
   - **Analysis phase:** LLM performs a one-time, costly, and comprehensive analysis on the new document format
     - Analyzes table design
     - Identifies footnote patterns
     - Extracts lab reference range formats
     - Highlights possible areas of confusion or ambiguity
   - **Generation phase:** System generates a complete AI tool for improved handling of peculiar formats
     - Custom system instructions
     - AI tool schema definition
     - Format-specific extraction rules
