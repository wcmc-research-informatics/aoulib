CREATE TABLE $TABLE_NAME$ (
	 [PMI ID] NVARCHAR(64) NULL 
	,[Biobank ID] NVARCHAR(64) NULL 
	,[Last Name] NVARCHAR(256) NULL 
	,[First Name] NVARCHAR(256) NULL 
	,[Date of Birth] DATE NULL 
	,[Language] NVARCHAR(32) NULL 
	,[Language of General Consent] NVARCHAR(32) NULL
    ,[Participant Status] NVARCHAR(28) NULL
	,[General Consent Status] NVARCHAR(2) NULL 
	,[General Consent Date] DATE NULL 
	,[EHR Consent Status] NVARCHAR(2) NULL 
	,[EHR Consent Date] DATE NULL 
	,[CABoR Consent Status] NVARCHAR(2) NULL 
	,[CABoR Consent Date] DATE NULL 
	,[Withdrawal Status] NVARCHAR(2) NULL 
	,[Withdrawal Reason] NVARCHAR(256) NULL
	,[Withdrawal Date] DATE NULL 
	,[Street Address] NVARCHAR(256) NULL 
	,[Street Address2] NVARCHAR(256) NULL
	,[City] NVARCHAR(128) NULL 
	,[State] NVARCHAR(128) NULL 
	,[ZIP] NVARCHAR(32) NULL 
	,[Email] NVARCHAR(256) NULL 
	,[Phone] NVARCHAR(32) NULL 
	,[Sex] NVARCHAR(32) NULL 
	,[Gender Identity] NVARCHAR(32) NULL 
	,[Race/Ethnicity] NVARCHAR(64) NULL 
	,[Education] NVARCHAR(128) NULL 
	,[Required PPI Surveys Complete] NVARCHAR(2) NULL 
	,[Completed Surveys] NVARCHAR(2) NULL 
	,[Basics PPI Survey Complete] NVARCHAR(2) NULL 
	,[Basics PPI Survey Completion Date] DATE NULL 
	,[Health PPI Survey Complete] NVARCHAR(2) NULL 
	,[Health PPI Survey Completion Date] DATE NULL 
	,[Lifestyle PPI Survey Complete] NVARCHAR(2) NULL 
	,[Lifestyle PPI Survey Completion Date] DATE NULL 
	,[Hist PPI Survey Complete] NVARCHAR(2) NULL 
	,[Hist PPI Survey Completion Date] DATE NULL 
	,[Meds PPI Survey Complete] NVARCHAR(2) NULL 
	,[Meds PPI Survey Completion Date] DATE NULL 
	,[Family PPI Survey Complete] NVARCHAR(2) NULL 
	,[Family PPI Survey Completion Date] DATE NULL 
	,[Access PPI Survey Complete] NVARCHAR(2) NULL 
	,[Access PPI Survey Completion Date] DATE NULL 
	,[Physical Measurements Status] NVARCHAR(2) NULL 
	,[Physical Measurements Completion Date] DATE NULL 
    ,[Physical Measurements Site] NVARCHAR(50) NULL
    ,[Paired Site] NVARCHAR(50) NULL
    ,[Paired Organization] NVARCHAR(50) NULL
	,[Samples for DNA Received] NVARCHAR(2) NULL 
	,[Biospecimens] NVARCHAR(10) NULL 
	,[8 mL SST Collected] NVARCHAR(2) NULL 
	,[8 mL SST Collection Date] DATE NULL 
	,[8 mL PST Collected] NVARCHAR(2) NULL 
	,[8 mL PST Collection Date] DATE NULL 
	,[4 mL Na-Hep Collected] NVARCHAR(2) NULL 
	,[4 mL Na-Hep Collection Date] DATE NULL 
	,[4 mL EDTA Collected] NVARCHAR(2) NULL 
	,[4 mL EDTA Collection Date] DATE NULL 
	,[1st 10 mL EDTA Collected] NVARCHAR(2) NULL 
	,[1st 10 mL EDTA Collection Date] DATE NULL 
	,[2nd 10 mL EDTA Collected] NVARCHAR(2) NULL 
	,[2nd 10 mL EDTA Collection Date] DATE NULL 
	,[Urine 10 mL Collected] NVARCHAR(2) NULL 
	,[Urine 10 mL Collection Date] DATE NULL 
	,[Saliva Collected] NVARCHAR(2) NULL 
	,[Saliva Collection Date] DATE NULL
    ,[Biospecimens Site] NVARCHAR(50) NULL
	,[2 mL EDTA Collected] NVARCHAR(2) NULL
	,[2 mL EDTA Collection Date] DATE NULL
	,[Cell-Free DNA Collected] NVARCHAR(2) NULL
	,[Cell-Free DNA Collection Date] DATE NULL
	,[Paxgene RNA Collected] NVARCHAR(2) NULL
	,[Paxgene RNA Collection Date] DATE NULL
	,[Urine 90 mL Collected] NVARCHAR(2) NULL
	,[Urine 90 mL Collection Date] DATE NULL
	,[DV-only EHR Sharing Status] NVARCHAR(2) NULL
	,[DV-only EHR Sharing Date] DATE NULL
	,[Login Phone] NVARCHAR(32) NULL
	,[Core Participant Date] DATETIME2 NULL
	,[enrollmentStatusCoreOrderedSampleTime] DATETIME2 NULL
	,[Biospecimen Status] [NVARCHAR](MAX) NULL
	,[4 mL EDTA Sample Order Status] [NVARCHAR](MAX) NULL
	,[Saliva Sample Order Status] [NVARCHAR](MAX) NULL
	,[gRoR Consent Status] [NVARCHAR](2) NULL
	,[gRoR Consent Date] DATETIME2 NULL
	,[COPE May PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE June PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE July PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE May PPI Survey Completion Date] DATETIME2 NULL
	,[COPE June PPI Survey Completion Date] DATETIME2 NULL
	,[COPE July PPI Survey Completion Date] DATETIME2 NULL
	,[income] NVARCHAR(32) NULL
	,[retentionEligibleStatus] NVARCHAR(32) NULL
	,[Consent Cohort] NVARCHAR(32) NULL
	,[Retention Status] NVARCHAR(2) NULL
	,[COPE Nov PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE Dec PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE Nov PPI Survey Completion Date] DATETIME2 NULL
	,[COPE Dec PPI Survey Completion Date] DATETIME2 NULL
	,[Date of First Primary Consent] DATE NULL
	,[Date of First EHR Consent] DATE NULL
	,[COPE Feb PPI Survey Complete] [NVARCHAR](2) NULL
	,[COPE Feb PPI Survey Completion Date] DATETIME2 NULL
	,[biospecimenCollectedSite] [NVARCHAR](MAX) NULL
	,[biospecimenSourceSite] [NVARCHAR](MAX) NULL
	,[enrollmentSite] [NVARCHAR](MAX) NULL
	,[numBaselineSamplesArrived] [NVARCHAR](MAX) NULL
	,[participantId] [NVARCHAR](MAX) NULL
	,[physicalMeasurementsFinalizedSite] [NVARCHAR](MAX) NULL
	,[sampleStatus1CFD9] [NVARCHAR](MAX) NULL
	,[sampleStatus1CFD9Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1ED02] [NVARCHAR](MAX) NULL
	,[sampleStatus1ED04] [NVARCHAR](MAX) NULL
	,[sampleStatus1ED04Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1ED10] [NVARCHAR](MAX) NULL
	,[sampleStatus1ED10Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1HEP4] [NVARCHAR](MAX) NULL
	,[sampleStatus1HEP4Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1PS08] [NVARCHAR](MAX) NULL
	,[sampleStatus1PST8] [NVARCHAR](MAX) NULL
	,[sampleStatus1PST8Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1PXR2] [NVARCHAR](MAX) NULL
	,[sampleStatus1PXR2Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1SAL] [NVARCHAR](MAX) NULL
	,[sampleStatus1SAL2] [NVARCHAR](MAX) NULL
	,[sampleStatus1SAL2Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1SALTime] [NVARCHAR](MAX) NULL
	,[sampleStatus1SS08] [NVARCHAR](MAX) NULL
	,[sampleStatus1SST8] [NVARCHAR](MAX) NULL
	,[sampleStatus1SST8Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1UR10] [NVARCHAR](MAX) NULL
	,[sampleStatus1UR10Time] [NVARCHAR](MAX) NULL
	,[sampleStatus1UR90] [NVARCHAR](MAX) NULL
	,[sampleStatus2ED10] [NVARCHAR](MAX) NULL
	,[sampleStatus2ED10Time] [NVARCHAR](MAX) NULL
	,[sampleStatus2PST8] [NVARCHAR](MAX) NULL
	,[sampleStatus2SST8] [NVARCHAR](MAX) NULL
	,[sampleStatusDV1SAL2] [NVARCHAR](MAX) NULL
	,[samplesToIsolateDNA] [NVARCHAR](MAX) NULL
	,[site] [NVARCHAR](MAX) NULL
	,[Summer Meeting Survey Complete] [NVARCHAR](2) NULL
	,[Summer Meeting Survey Complete Date] DATETIME2 NULL
	,[Fall Meeting Survey Complete] [NVARCHAR](2) NULL
	,[Fall Meeting Survey Complete Date] DATETIME2 NULL
	,[Personal & Family Hx PPI Survey Complete] [NVARCHAR](2) NULL
	,[Personal & Family Hx PPI Survey Completion Date] DATETIME2 NULL
	,[SDOH PPI Survey Complete] [NVARCHAR](2) NULL
	,[SDOH PPI Survey Completion Date] DATETIME2 NULL
	,[Winter Minute PPI Survey Complete] [NVARCHAR](2) NULL
	,[Winter Minute PPI Survey Completion Date] DATETIME2 NULL
	,[Digital Health Consent] [VARCHAR](MAX) NULL
    ,[New Year Minute PPI Survey Complete] [NVARCHAR](2) NULL
	,[New Year Minute PPI Survey Completion Date] DATETIME2 NULL
    ,[Enrollment Site] [NVARCHAR](MAX) NULL
    ,[Physical Measurements Collection Type] [NVARCHAR](MAX) NULL
    ,[ID Verification Date] DATETIME2 NULL
    ,[Incentive Date] DATETIME2 NULL
    ,[Remote Physical Measurements Status] [NVARCHAR](MAX) NULL
    ,[Remote Physical Measurements Completion Date] DATETIME2 NULL
    ,[Clinic Physical Measurements Status] [NVARCHAR](MAX) NULL
    ,[Clinic Physical Measurements Completion Date] DATETIME2 NULL
    ,[Clinic Physical Measurements Site] [NVARCHAR](MAX) NULL
    ,[Clinic Physical Measurements Date] DATETIME2 NULL
    ,[Clinic Physical Measurements Creation Site] [NVARCHAR](MAX) NULL
    ,[Date of Primary Re-Consent] DATETIME2 NULL
    ,[Date of EHR Re-Consent] DATETIME2 NULL
)
