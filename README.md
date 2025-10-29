# Chicago-accident-Analysis
Project about Chicago road accident and answering critical question on how does accident occur. 
Decision Support Project: Crash Data Analysis 🚗💡

Project Overview

This repository documents the work completed for the Decision Support Project at the University of Pisa (A.Y. 2024/2025). The project focuses on designing, implementing, and querying a robust Data Warehouse (DW) and OLAP Cube to analyze complex transportation crash data.

The primary goal is to transform raw operational data into actionable intelligence, enabling stakeholders to make data-driven decisions regarding public safety, infrastructure investment, and risk mitigation related to vehicle crashes.



**Project Phases**

The project was divided into two main parts, covering the full life cycle from raw data to analytical insight.

Part I: Data Warehouse Implementation

Data Understanding & Cleaning: Initial assessment of the dataset, identifying quality issues, and performing necessary cleaning operations.

DW Schema Design: Designing the dimensional model (Star/Snowflake Schema) appropriate for crash data, defining Fact Tables (e.g., Crash Events) and Dimension Tables (e.g., Time, Location, Vehicle, Cause).

Data Preparation & Loading: Developing Python scripts and SSIS packages for Extract, Transform, and Load (ETL) operations to populate the DW tables efficiently.

Part II: OLAP Cube Development & Analysis

Cube Creation: Building the multi-dimensional cube on top of the DW schema using SSAS.

Hierarchical Dimensions: Defining natural hierarchies within dimensions (e.g., Date -> Year -> Quarter -> Month, Location -> Country -> City -> Street) to facilitate drill-down and roll-up analysis.

Measure Definition: Creating key measures for analytical processing, including:

Total Damage Cost

Crash Count

Maximum Vehicle Type per Year

Key Analytical Findings (MDX Assignments)

The cube was utilized to perform complex queries addressing specific decision-support questions:

Weighted Crash Cause Analysis: Calculated a Weighted Crash Cause Count by assigning priority weights (e.g., 2 for primary contributory cause, 1 for secondary contributory cause) to ensure a prioritized evaluation of crash causes.

Damage Cost by Cause: Identified the Overall Most Frequent Crash Cause across all years and calculated its associated Total Damage Cost.

Geographical Distribution: Generated a dashboard showing the geographical distribution of total damage costs segmented by different vehicle categories.

👨‍💻 Author

This project was authored by:

Hamse Hassan Adnan

Feel free to connect or explore the methodologies used within this project.
