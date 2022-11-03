import sys
import dateutil.parser
import pytz

# See notes at bottom of file.

__all__ = ['into_hp_row']

#------------------------------------------------------------------------------
# utilities

def str2func(funcname):
  this = sys.modules[__name__]
  return getattr(this, funcname)

#------------------------------------------------------------------------------
# one-to-one mappings and functions

mappings_one_to_one = [

  {'hp':'PMI ID', 'api':'participantId'},
  {'hp':'Biobank ID', 'api':'biobankId'}, 
  {'hp':'Last Name', 'api':'lastName'}, 
  {'hp':'First Name', 'api':'firstName'}, 
  {'hp':'Date of Birth', 'api':'dateOfBirth', 'func':'api2hp_date'}, 
  {'hp':'Language', 'api':'language', 'func':'api2hp_cb'}, # WQC 321; deprecated; always blank. 
  {'hp':'Language of General Consent', 'api':'primaryLanguage', 'func':'api2hp_language'},

  {'hp':'Participant Status', 'api':'enrollmentStatus', 'func':'api2hp_cb'}, # WQC 322
  {'hp':'General Consent Status', 'api':'consentForStudyEnrollment', 'func':'api2hp_status'}, # WQC 257, 323
  {'hp':'General Consent Date', 'api':'consentForStudyEnrollmentAuthored', 'func':'api2hp_datetime'}, # WQC 258, 324
  {'hp':'EHR Consent Status', 'api':'consentForElectronicHealthRecords', 'func':'api2hp_status'}, # WQC 325
  {'hp':'EHR Consent Date', 'api':'consentForElectronicHealthRecordsAuthored', 'func':'api2hp_datetime'}, # WQC 326
  {'hp':'CABoR Consent Status', 'api':'consentForCABoR', 'func':'api2hp_status'}, 
  {'hp':'CABoR Consent Date', 'api':'consentForCABoRTime', 'func':'api2hp_datetime'},
  {'hp':'Withdrawal Status', 'api':'withdrawalStatus', 'func':'api2hp_withdrawal'}, 
  {'hp':'Withdrawal Reason', 'api':'withdrawalReason', 'func':'api2hp_cb'},  # WQC 301, 374
  {'hp':'Withdrawal Date', 'api':'withdrawalTime', 'func':'api2hp_datetime'}, # WQC 330

  {'hp':'Street Address', 'api':'streetAddress', 'func':'api2hp_basic'},
  # Note about streetAddress2: the API will leave this out if empty.
  # HealthPro checks for this and returns empty string.
  {'hp':'Street Address2', 'api':'streetAddress2', 'func':'api2hp_basic'}, # WQC 381 
  {'hp':'City', 'api':'city', 'func':'api2hp_basic'},
  {'hp':'State', 'api':'state', 'func':'api2hp_state'},
  {'hp':'ZIP', 'api':'zipCode', 'func':'api2hp_basic'},
  {'hp':'Email', 'api':'email', 'func':'api2hp_basic'},
  {'hp':'Phone', 'api':'phoneNumber', 'func':'api2hp_basic'},
  {'hp':'Sex', 'api':'sex', 'func':'api2hp_cb'}, # WQC 337
  {'hp':'Gender Identity', 'api':'genderIdentity', 'func':'api2hp_cb'}, # WQC 338
  {'hp':'Race/Ethnicity', 'api':'race', 'func':'api2hp_cb'}, # WQC 339
  {'hp':'Education', 'api':'education', 'func':'api2hp_cb'}, # WQC 340

  {'hp':'Required PPI Surveys Complete', 'api':'numCompletedBaselinePPIModules', 'func':'api2hp_required_surveys_completed'},
  {'hp':'Completed Surveys', 'api':'numCompletedPPIModules', 'func':'api2hp_completed_or_0'}, # WQC 342

  # Surveys processed in WQC via for-loops starting line 278 (headers), 344 (values)
  # See also: $surveys data member in WQ class. (line 206).
  {'hp':'Basics PPI Survey Complete', 'api':'questionnaireOnTheBasics', 'func':'api2hp_status'}, 
  # Regarding "questionnaireOnTheBasicsTime" vs "questionnaireOnTheBasicsAuthored" (and similar):
  # (which both show up api data): code at WQC line 346 uses "Time" as suffix.
  # Additionally, the 'authored' versions are not mentioned in the field descriptions in the README.
  {'hp':'Basics PPI Survey Completion Date', 'api':'questionnaireOnTheBasicsTime', 'func':'api2hp_datetime'},
  {'hp':'Health PPI Survey Complete', 'api':'questionnaireOnOverallHealth', 'func':'api2hp_status'},
  {'hp':'Health PPI Survey Completion Date', 'api':'questionnaireOnOverallHealthTime', 'func':'api2hp_datetime'},
  {'hp':'Lifestyle PPI Survey Complete', 'api':'questionnaireOnLifestyle', 'func':'api2hp_status'},
  {'hp':'Lifestyle PPI Survey Completion Date', 'api':'questionnaireOnLifestyleTime', 'func':'api2hp_datetime'},
  {'hp':'Hist PPI Survey Complete', 'api':'questionnaireOnMedicalHistory', 'func':'api2hp_status'},
  {'hp':'Hist PPI Survey Completion Date', 'api':'questionnaireOnMedicalHistoryTime', 'func':'api2hp_datetime'},
  {'hp':'Meds PPI Survey Complete', 'api':'questionnaireOnMedications', 'func':'api2hp_status'},
  {'hp':'Meds PPI Survey Completion Date', 'api':'questionnaireOnMedicationsTime', 'func':'api2hp_datetime'},
  {'hp':'Family PPI Survey Complete', 'api':'questionnaireOnFamilyHealth', 'func':'api2hp_status'},
  {'hp':'Family PPI Survey Completion Date', 'api':'questionnaireOnFamilyHealthTime', 'func':'api2hp_datetime'},
  {'hp':'Access PPI Survey Complete', 'api':'questionnaireOnHealthcareAccess', 'func':'api2hp_status'},
  {'hp':'Access PPI Survey Completion Date', 'api':'questionnaireOnHealthcareAccessTime', 'func':'api2hp_datetime'},

  {'hp':'Physical Measurements Status', 'api':'physicalMeasurementsStatus', 'func':'api2hp_completed'}, # WQC 289, 
  {'hp':'Physical Measurements Completion Date', 'api':'physicalMeasurementsFinalizedTime', 'func':'api2hp_datetime'}, # WQC 290, 356
  #{'hp':'Physical Measurements Site', 'api':'evaluationFinalizedSite'},  # WQC 293, 359
  {'hp':'Physical Measurements Site', 'api':'physicalMeasurementsFinalizedSite', 'func':'api2hp_site'},  # WQC 293, 359

  {'hp':'Paired Site', 'api':'site', 'func':'api2hp_site'}, # WQC 291, 357
  {'hp':'Paired Organization', 'api':'organization'}, # WQC 292, 358

  {'hp':'Samples for DNA Received', 'api':'samplesToIsolateDNA', 'func':'api2hp_received'}, # WQC 294, 360
  {'hp':'Biospecimens', 'api':'numBaselineSamplesArrived', 'func':'api2hp_completed_or_0'}, # WQC 295, 361

  # Specific biospecimen-related fields constructed using for-loop
  # in WQC line 296-299 (headers), line 362 (values).
  # See WQ data member $samples line 216.
  # See also: one_to_many mappings below, and WQ $samplesAlias data member line 231.

  {'hp':'4 mL Na-Hep Collected', 'api':'sampleStatus1HEP4', 'func':'api2hp_received'},
  {'hp':'4 mL Na-Hep Collection Date', 'api':'sampleStatus1HEP4Time', 'func':'api2hp_datetime'},

  {'hp':'4 mL EDTA Collected', 'api':'sampleStatus1ED04', 'func':'api2hp_received'},
  {'hp':'4 mL EDTA Collection Date', 'api':'sampleStatus1ED04Time', 'func':'api2hp_datetime'},

  {'hp':'1st 10 mL EDTA Collected', 'api':'sampleStatus1ED10', 'func':'api2hp_received'},
  {'hp':'1st 10 mL EDTA Collection Date', 'api':'sampleStatus1ED10Time', 'func':'api2hp_datetime'},

  {'hp':'2nd 10 mL EDTA Collected', 'api':'sampleStatus2ED10', 'func':'api2hp_received'},
  {'hp':'2nd 10 mL EDTA Collection Date', 'api':'sampleStatus2ED10Time', 'func':'api2hp_datetime'},

  {'hp':'Urine 10 mL Collected', 'api':'sampleStatus1UR10', 'func':'api2hp_received'},
  {'hp':'Urine 10 mL Collection Date', 'api':'sampleStatus1UR10Time', 'func':'api2hp_datetime'},

  # WQC 300, 373 references an 'orderCreatedSite'; however the docs
  # mention 4 different biospecimen site fields; the closest one seems to be:
  # biospecimenSourceSite: "the site where biospecimens were initially created for the participant"
  {'hp':'Biospecimens Site', 'api':'biospecimenSourceSite', 'func':'api2hp_site'}, 

  {'hp':'2 mL EDTA Collected', 'api':'sampleStatus1ED02', 'func':'api2hp_received'},
  {'hp':'2 mL EDTA Collection Date', 'api':'sampleStatus1ED02Time', 'func':'api2hp_datetime'},

  {'hp':'Cell-Free DNA Collected', 'api':'sampleStatus1CFD9', 'func':'api2hp_received'},
  {'hp':'Cell-Free DNA Collection Date', 'api':'sampleStatus1CFD9Time', 'func':'api2hp_datetime'},

  {'hp':'Paxgene RNA Collected', 'api':'sampleStatus1PXR2', 'func':'api2hp_received'},
  {'hp':'Paxgene RNA Collection Date', 'api':'sampleStatus1PXR2Time', 'func':'api2hp_datetime'},

  {'hp':'Urine 90 mL Collected', 'api':'sampleStatus1UR90', 'func':'api2hp_received'},
  {'hp':'Urine 90 mL Collection Date', 'api':'sampleStatus1UR90Time', 'func':'api2hp_datetime'},

  {'hp':'DV-only EHR Sharing Status', 'api':'consentForDvElectronicHealthRecordsSharing', 'func':'api2hp_status'},
  {'hp':'DV-only EHR Sharing Date', 'api':'consentForDvElectronicHealthRecordsSharingTime', 'func':'api2hp_datetime'},

  {'hp':'Login Phone', 'api':'loginPhoneNumber', 'func':'api2hp_basic'},

  # "Core Participant Date" added Feb 2020. See WQC 353/438.
  {'hp':'Core Participant Date', 'api':'enrollmentStatusCoreStoredSampleTime', 'func':'api2hp_datetime'},
  # Added Feb 2020; no HP equivalent.
  {'hp':'enrollmentStatusCoreOrderedSampleTime', 'api':'enrollmentStatusCoreOrderedSampleTime', 'func':'api2hp_datetime'},
  {'hp':'Biospecimen Status', 'api':'biospecimenStatus', 'func':'api2hp_basic'},
  {'hp':'4 mL EDTA Sample Order Status', 'api':'sampleOrderStatus1ED04', 'func':'api2hp_basic'},
  {'hp':'gRoR Consent Status', 'api':'consentForGenomicsROR', 'func':'api2hp_status'},
  {'hp':'gRoR Consent Date', 'api':'consentForGenomicsRORAuthored', 'func':'api2hp_datetime'},

  # COPE fields
  {'hp':'COPE May PPI Survey Complete', 'api':'questionnaireOnCopeMay', 'func':'api2hp_status'},
  {'hp':'COPE May PPI Survey Completion Date', 'api':'questionnaireOnCopeMayAuthored', 'func':'api2hp_datetime'},
  {'hp':'COPE June PPI Survey Complete', 'api':'questionnaireOnCopeJune', 'func':'api2hp_status'},
  {'hp':'COPE June PPI Survey Completion Date', 'api':'questionnaireOnCopeJuneAuthored', 'func':'api2hp_datetime'},
  {'hp':'COPE July PPI Survey Complete', 'api':'questionnaireOnCopeJuly', 'func':'api2hp_status'},
  {'hp':'COPE July PPI Survey Completion Date', 'api':'questionnaireOnCopeJulyAuthored', 'func':'api2hp_datetime'},
  {'hp':'income', 'api':'income', 'func':'api2hp_basic'},
  {'hp':'retentionEligibleStatus', 'api':'retentionEligibleStatus', 'func':'api2hp_basic'},

  # "Retention Status" field 
  {'hp':'Retention Status', 'api':'retentionType', 'func':'api2hp_retention_status'},

  # Additional COPE fields
  {'hp':'COPE Nov PPI Survey Complete', 'api':'questionnaireOnCopeNov', 'func':'api2hp_status'},
  {'hp':'COPE Nov PPI Survey Completion Date', 'api':'questionnaireOnCopeNovAuthored', 'func':'api2hp_datetime'},
  {'hp':'COPE Dec PPI Survey Complete', 'api':'questionnaireOnCopeDec', 'func':'api2hp_status'},
  {'hp':'COPE Dec PPI Survey Completion Date', 'api':'questionnaireOnCopeDecAuthored', 'func':'api2hp_datetime'},

  # "Date of First * Consent" fields
  {'hp':'Date of First Primary Consent', 'api':'consentForStudyEnrollmentFirstYesAuthored', 'func':'api2hp_datetime'},
  {'hp':'Date of First EHR Consent', 'api':'consentForElectronicHealthRecordsFirstYesAuthored', 'func':'api2hp_datetime'},

  # Feb 2021 COPE survey fields - NIHPMI-551
  {'hp': 'COPE Feb PPI Survey Complete', 'api': 'questionnaireOnCopeFeb', 'func': 'api2hp_status'},
  {'hp': 'COPE Feb PPI Survey Completion Date', 'api': 'questionnaireOnCopeFebAuthored', 'func':'api2hp_datetime'},

  # NIHPMI-546 lab fields
  {'hp':'biospecimenCollectedSite', 'api':'biospecimenCollectedSite', 'func':'api2hp_basic'},
  {'hp':'biospecimenSourceSite', 'api':'biospecimenSourceSite', 'func':'api2hp_basic'},
  {'hp':'enrollmentSite', 'api':'enrollmentSite', 'func':'api2hp_basic'},
  {'hp':'numBaselineSamplesArrived', 'api':'numBaselineSamplesArrived', 'func':'api2hp_basic'},
  {'hp':'participantId', 'api':'participantId', 'func':'api2hp_basic'},
  {'hp':'physicalMeasurementsFinalizedSite', 'api':'physicalMeasurementsFinalizedSite', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1CFD9', 'api':'sampleStatus1CFD9', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1CFD9Time', 'api':'sampleStatus1CFD9Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1ED02', 'api':'sampleStatus1ED02', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1ED04', 'api':'sampleStatus1ED04', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1ED04Time', 'api':'sampleStatus1ED04Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1ED10', 'api':'sampleStatus1ED10', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1ED10Time', 'api':'sampleStatus1ED10Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1HEP4', 'api':'sampleStatus1HEP4', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1HEP4Time', 'api':'sampleStatus1HEP4Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1PS08', 'api':'sampleStatus1PS08', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1PST8', 'api':'sampleStatus1PST8', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1PST8Time', 'api':'sampleStatus1PST8Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1PXR2', 'api':'sampleStatus1PXR2', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1PXR2Time', 'api':'sampleStatus1PXR2Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SAL', 'api':'sampleStatus1SAL', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SAL2', 'api':'sampleStatus1SAL2', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SAL2Time', 'api':'sampleStatus1SAL2Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SALTime', 'api':'sampleStatus1SALTime', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SS08', 'api':'sampleStatus1SS08', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SST8', 'api':'sampleStatus1SST8', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1SST8Time', 'api':'sampleStatus1SST8Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1UR10', 'api':'sampleStatus1UR10', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1UR10Time', 'api':'sampleStatus1UR10Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus1UR90', 'api':'sampleStatus1UR90', 'func':'api2hp_basic'},
  {'hp':'sampleStatus2ED10', 'api':'sampleStatus2ED10', 'func':'api2hp_basic'},
  {'hp':'sampleStatus2ED10Time', 'api':'sampleStatus2ED10Time', 'func':'api2hp_basic'},
  {'hp':'sampleStatus2PST8', 'api':'sampleStatus2PST8', 'func':'api2hp_basic'},
  {'hp':'sampleStatus2SST8', 'api':'sampleStatus2SST8', 'func':'api2hp_basic'},
  {'hp':'sampleStatusDV1SAL2', 'api':'sampleStatusDV1SAL2', 'func':'api2hp_basic'},
  {'hp':'samplesToIsolateDNA', 'api':'samplesToIsolateDNA', 'func':'api2hp_basic'},
  {'hp':'site', 'api':'site', 'func':'api2hp_basic'},
  
  # NIHPMI-570 Summer and Fall Surveys
  {'hp':'Summer Meeting Survey Complete', 'api':'questionnaireOnCopeVaccineMinute1', 'func':'api2hp_status'},
  {'hp':'Summer Meeting Survey Complete Date', 'api':'questionnaireOnCopeVaccineMinute1Authored', 'func':'api2hp_datetime'},
  {'hp':'Fall Meeting Survey Complete', 'api':'questionnaireOnCopeVaccineMinute2', 'func':'api2hp_status'},
  {'hp':'Fall Meeting Survey Complete Date', 'api':'questionnaireOnCopeVaccineMinute2Authored', 'func':'api2hp_datetime'},

  # NIHPMI-574 Personal & Family Hx, SDOH, Winter Minute, New Year Minute Surveys, and Digital Health Consent
  {'hp':'Personal & Family Hx PPI Survey Complete', 'api':'questionnaireOnPersonalAndFamilyHealthHistory', 'func':'api2hp_status'},
  {'hp':'Personal & Family Hx PPI Survey Completion Date', 'api':'questionnaireOnPersonalAndFamilyHealthHistoryAuthored', 'func':'api2hp_datetime'},
  {'hp':'SDOH PPI Survey Complete', 'api':'questionnaireOnSocialDeterminantsOfHealth', 'func':'api2hp_status'},
  {'hp':'SDOH PPI Survey Completion Date', 'api':'questionnaireOnSocialDeterminantsOfHealthAuthored', 'func':'api2hp_datetime'},
  {'hp':'Winter Minute PPI Survey Complete', 'api':'questionnaireOnCopeVaccineMinute3', 'func':'api2hp_status'},
  {'hp':'Winter Minute PPI Survey Completion Date', 'api':'questionnaireOnCopeVaccineMinute3Authored', 'func':'api2hp_datetime'},
  {'hp':'Digital Health Consent', 'api':'digitalHealthSharingStatus', 'func':'api2hp_into_str'},
  {'hp':'New Year Minute PPI Survey Complete', 'api':'questionnaireOnCopeVaccineMinute4', 'func':'api2hp_status'},
  {'hp':'New Year Minute PPI Survey Completion Date', 'api':'questionnaireOnCopeVaccineMinute4Authored', 'func':'api2hp_datetime'},
  {'hp':'Enrollment Site', 'api':'enrollmentSite', 'func':'api2hp_into_str'},
  {'hp':'Physical Measurements Collection Type', 'api':'physicalMeasurementsCollectType', 'func':'api2hp_into_str'},
  {'hp':'ID Verification Date', 'api':'onSiteIdVerificationTime', 'func':'api2hp_datetime'},
  {'hp':'Incentive Date', 'api':'participantIncentives', 'func':'api2hp_datetime'},
  {'hp':'Remote Physical Measurements Status', 'api':'selfReportedPhysicalMeasurementsStatus', 'func':'api2hp_into_str'},
  {'hp':'Remote Physical Measurements Completion Date', 'api':'selfReportedPhysicalMeasurementsAuthored', 'func':'api2hp_datetime'},
  {'hp':'Clinic Physical Measurements Status', 'api':'clinicPhysicalMeasurementsStatus', 'func':'api2hp_into_str'},
  {'hp':'Clinic Physical Measurements Completion Date', 'api':'clinicPhysicalMeasurementsFinalizedTime', 'func':'api2hp_datetime'},
  {'hp':'Clinic Physical Measurements Site', 'api':'clinicPhysicalMeasurementsFinalizedSite', 'func':'api2hp_into_str'},
  {'hp':'Clinic Physical Measurements Date', 'api':'clinicPhysicalMeasurementsTime', 'func':'api2hp_datetime'},
  {'hp':'Clinic Physical Measurements Creation Site', 'api':'clinicPhysicalMeasurementsCreatedSite', 'func':'api2hp_into_str'},
  {'hp':'Date of Primary Re-Consent', 'api':'reconsentForStudyEnrollmentAuthored', 'func':'api2hp_datetime'},
  {'hp':'Date of EHR Re-Consent', 'api':'reconsentForElectronicHealthRecordsAuthored', 'func':'api2hp_datetime'},
]

def api2hp_basic(x):
  if x == 'UNSET': return ''
  else: return x

def api2hp_completed_or_0(x):
  out = str(x)
  if x == '': return '0'
  else: return out

def api2hp_date(x):
  '''yyyy-MM-dd into dd/MM/yyyy'''
  if not x or x.strip() == '': return ''
  return dateutil.parser.parse(x).strftime('%m/%d/%Y')

def api2hp_datetime(x):
  '''yyyy-MM-ddThh:mm:ss into dd/MM/yyyy [h]h:mm {am|pm}
  We convert from UTC to our timezone b/c that's what HP does.
  Note that target tz of US/Eastern is hardcoded here (change if desired).
  We don't completely match (HP also strips leading zero from month
  and day) but close enough.'''
  if not x or x.strip() == '': return ''
  dt_obj = dateutil.parser.parse(x)
  dt_obj = dt_obj.replace(tzinfo=pytz.utc)
  tz_eastern = pytz.timezone('US/Eastern')
  # Next line does the following:
  # - shift timezone from UTC to Eastern
  # - format into the almost (but not quite) the desired HP style datetime format.
  return dt_obj.astimezone(tz=tz_eastern).strftime('%m/%d/%Y %I:%M %p')
  # If you wanted you could also use the version below in order to:
  # - remove leading zero from hour portion
  # - change "AM" / "PM" to "am" / "pm" with lower()
  # return dt_obj.astimezone(tz=tz_eastern).strftime('%m/%d/%Y %I:%M %p').replace(' 0', ' ').lower()

def api2hp_language(x):
  '''Converts API-style language string into full name of language.
  Argument: x: API value.
  Comments:
  - Unsure where in HP source this conversion is done.
  - Determined via data review (also, see HP CodeBook).
  - (That said, note that these are the only two langauges handled per WQ
    $filtersDisabled method.)'''
  if x == 'UNSET': return ''
  if x == 'en': return 'English'
  if x == 'es': return 'Spanish'
  return x

def api2hp_status(x):
  '''Many status-related fields use this conversion.
  Argument: x: API value.
  Comment: see WQ csvStatusFromSubmitted method.'''
  if x == 'SUBMITTED': return '1'
  if x == 'SUBMITTED_NOT_SURE': return '2' 
  return '0'

def api2hp_completed(x):
  '''Argument: x: API field.
  Comment: see WQC line 355'''
  if x == 'COMPLETED': return '1'
  return '0'

def api2hp_received(x):
  '''Argument: x: API value.
  Comment: See WQC lines 360, 370.'''
  if x == 'RECEIVED': return '1'
  return '0'

def api2hp_withdrawal(x):
  '''This replicates inline logic at WQC exportAction line 329:
        $participant->withdrawalStatus == 'NO_USE' ? '1' : '0',
  '''
  if x == 'NO_USE': return '1'
  return '0'

def api2hp_state(x):
  if x == 'UNSET': return ''
  else: return x.replace('PIIState_', '')

def api2hp_required_surveys_completed(x):
  '''This function replicates the inline logic at WQC line 341.'''
  if x == 3: return '1'
  return '0'

def api2hp_into_str(x):
  return str(x)

def api2hp_site(x):
  if x == 'UNSET': return ''
  else: return x.replace('hpo-site-', '')

def api2hp_retention_status(x):
    lookup = {
      'PASSIVE': '1',
      'ACTIVE': '2',
      'ACTIVE_AND_PASSIVE': '3',
      'UNSET': '0'
    }
    return lookup.get(x, '')

#-------------------------------------------------------------------------------
# codebook 

# This is replicated from HealthPro's CodeBook class.

codebook = {
  'UNSET' : '',
  'UNMAPPED' : '',
  'PREFER_NOT_TO_SAY' : 'Prefer Not To Answer',
  'PMI_Skip' : 'Skip',
  'PMI_PreferNotToAnswer' : 'Prefer Not To Answer',
  'PMI_Other' : 'Other',
  'PMI_Unanswered' : 'Unanswered',
  'PMI_DontKnow' : 'Don\'t Know',
  'PMI_NotSure' : 'Not Sure',
  'RecontactMethod_HousePhone' : 'House Phone',
  'RecontactMethod_CellPhone' : 'Cell Phone',
  'RecontactMethod_Email' : 'Email',
  'RecontactMethod_Address' : 'Physical Address',
  'NO_CONTACT' : 'No Contact',
  'SexAtBirth_Male' : 'Male',
  'SexAtBirth_Female' : 'Female',
  'SexAtBirth_Intersex' : 'Intersex',
  'SexAtBirth_None' : 'Other',
  'SexAtBirth_SexAtBirthNoneOfThese' : 'Other',
  'GenderIdentity_Man' : 'Man',
  'GenderIdentity_Woman' : 'Woman',
  'GenderIdentity_NonBinary' : 'Non-binary',
  'GenderIdentity_Transgender' : 'Transgender',
  'GenderIdentity_AdditionalOptions' : 'Other',
  'GenderIdentity_MoreThanOne' : 'More Than One Gender Identity',
  'SexualOrientation_Straight' : 'Straight',
  'SexualOrientation_Gay' : 'Gay',
  'SexualOrientation_Lesbian' : 'Lesbian',
  'SexualOrientation_Bisexual' : 'Bisexual',
  'SexualOrientation_None' : 'Other',
  'SpokenWrittenLanguage_Arabic' : 'Arabic',
  'SpokenWrittenLanguage_Bengali' : 'Bengali',
  'SpokenWrittenLanguage_Czech' : 'Czech',
  'SpokenWrittenLanguage_Danish' : 'Danish',
  'SpokenWrittenLanguage_German' : 'German',
  'SpokenWrittenLanguage_GermanAustria' : 'German (Austria)',
  'SpokenWrittenLanguage_GermanSwitzerland' : 'German (Switzerland)',
  'SpokenWrittenLanguage_GermanGermany' : 'German (Germany)',
  'SpokenWrittenLanguage_Greek' : 'Greek',
  'SpokenWrittenLanguage_English' : 'English',
  'SpokenWrittenLanguage_EnglishAustralia' : 'English (Australia)',
  'SpokenWrittenLanguage_EnglishCanada' : 'English (Canada)',
  'SpokenWrittenLanguage_EnglishGreatBritain' : 'English (Great Britain)',
  'SpokenWrittenLanguage_EnglishIndia' : 'English (India)',
  'SpokenWrittenLanguage_EnglishNewZeland' : 'English (New Zeland)',
  'SpokenWrittenLanguage_EnglishSingapore' : 'English (Singapore)',
  'SpokenWrittenLanguage_EnglishUnitedStates' : 'English (United States)',
  'SpokenWrittenLanguage_Spanish' : 'Spanish',
  'SpokenWrittenLanguage_SpanishArgentina' : 'Spanish (Argentina)',
  'SpokenWrittenLanguage_SpanishSpain' : 'Spanish (Spain)',
  'SpokenWrittenLanguage_SpanishUruguay' : 'Spanish (Uruguay)',
  'SpokenWrittenLanguage_Finnish' : 'Finnish',
  'SpokenWrittenLanguage_French' : 'French',
  'SpokenWrittenLanguage_FrenchBelgium' : 'French (Belgium)',
  'SpokenWrittenLanguage_FrenchSwitzerland' : 'French (Switzerland)',
  'SpokenWrittenLanguage_FrenchFrance' : 'French (France)',
  'SpokenWrittenLanguage_Frysian' : 'Frysian',
  'SpokenWrittenLanguage_FrysianNetherlands' : 'Frysian (Netherlands)',
  'SpokenWrittenLanguage_Hindi' : 'Hindi',
  'SpokenWrittenLanguage_Croatian' : 'Croatian',
  'SpokenWrittenLanguage_Italian' : 'Italian',
  'SpokenWrittenLanguage_ItalianSwitzerland' : 'Italian (Switzerland)',
  'SpokenWrittenLanguage_ItalianItaly' : 'Italian (Italy)',
  'SpokenWrittenLanguage_Japanese' : 'Japanese',
  'SpokenWrittenLanguage_Korean' : 'Korean',
  'SpokenWrittenLanguage_Dutch' : 'Dutch',
  'SpokenWrittenLanguage_DutchBelgium' : 'Dutch (Belgium)',
  'SpokenWrittenLanguage_DutchNetherlands' : 'Dutch (Netherlands)',
  'SpokenWrittenLanguage_Norwegian' : 'Norwegian',
  'SpokenWrittenLanguage_NorwegianNorway' : 'Norwegian (Norway)',
  'SpokenWrittenLanguage_Punjabi' : 'Punjabi',
  'SpokenWrittenLanguage_Portuguese' : 'Portuguese',
  'SpokenWrittenLanguage_PortugueseBrazil' : 'Portuguese (Brazil)',
  'SpokenWrittenLanguage_Russian' : 'Russian',
  'SpokenWrittenLanguage_RussianRussia' : 'Russian (Russia)',
  'SpokenWrittenLanguage_Serbian' : 'Serbian',
  'SpokenWrittenLanguage_SerbianSerbia' : 'Serbian (Serbia)',
  'SpokenWrittenLanguage_Swedish' : 'Swedish',
  'SpokenWrittenLanguage_SwedishSweden' : 'Swedish (Sweden)',
  'SpokenWrittenLanguage_Telegu' : 'Telegu',
  'SpokenWrittenLanguage_Chinese' : 'Chinese',
  'SpokenWrittenLanguage_ChineseChina' : 'Chinese (China)',
  'SpokenWrittenLanguage_ChineseHongKong' : 'Chinese (Hong Kong)',
  'SpokenWrittenLanguage_ChineseSingapore' : 'Chinese (Singapore)',
  'SpokenWrittenLanguage_ChineseTaiwan' : 'Chinese (Taiwan)',
  'AnnualIncome_less10k' : 'Less than $10,000',
  'AnnualIncome_10k25k' : '$10,000- $24,999',
  'AnnualIncome_25k35k' : '$25,000- $34,999',
  'AnnualIncome_35k50k' : '$35,000- $49,999',
  'AnnualIncome_50k75k' : '$50,000- $74,999',
  'AnnualIncome_75k100k' : '$75,000- $99,999',
  'AnnualIncome_100k150k' : '$100,000- $149,999',
  'AnnualIncome_150k200k' : '$150,000- $199,999',
  'AnnualIncome_more200k' : '$200,000 or more',
  'HighestGrade_NeverAttended' : 'Never attended school or only attended kindergarten',
  'HighestGrade_OneThroughFour' : 'Grades 1 through 4 (Primary)',
  'HighestGrade_FiveThroughEight' : 'Grades 5 through 8 (Secondary)',
  'HighestGrade_NineThroughEleven' : 'Grades 9 through 11 (Some high school)',
  'HighestGrade_TwelveOrGED' : 'Grade 12 or GED (High school graduate)',
  'HighestGrade_CollegeOnetoThree' : 'College 1 to 3 years (Some college or technical school)',
  'HighestGrade_CollegeGraduate' : 'College 4 years or more (College graduate)',
  'HighestGrade_AdvancedDegree' : 'Advanced degree (Master\'s, Doctorate, etc.)',
  'AMERICAN_INDIAN_OR_ALASKA_NATIVE' : 'American Indian / Alaska Native',
  'BLACK_OR_AFRICAN_AMERICAN' : 'Black or African American',
  'ASIAN' : 'Asian',
  'NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER' : 'Native Hawaiian or Other Pacific Islander',
  'WHITE' : 'White',
  'HISPANIC_LATINO_OR_SPANISH' : 'Hispanic, Latino, or Spanish',
  'MIDDLE_EASTERN_OR_NORTH_AFRICAN' : 'Middle Eastern or North African',
  'HLS_AND_WHITE' : 'H/L/S and White',
  'HLS_AND_BLACK' : 'H/L/S and Black',
  'HLS_AND_ONE_OTHER_RACE' : 'H/L/S and one other race',
  'HLS_AND_MORE_THAN_ONE_OTHER_RACE' : 'H/L/S and more than one other race',
  'MORE_THAN_ONE_RACE' : 'More than one race',
  'OTHER_RACE' : 'Other',
  'INTERESTED' : 'Participant',
  'MEMBER' : 'Fully Consented',
  'FULL_PARTICIPANT' : 'Core Participant',
  'en' : 'English',
  'es' : 'Spanish'
}

def api2hp_cb(x):
  '''Use codebook to transform value.'''
  return codebook.get(x, '')

#------------------------------------------------------------------------------
# one-to-many mappings

'''
One to many mappings
--------------------
For more info, see:
  - WQC 362-372. loops through specimen values
    and when needed, determines value for 1-to-many items.
  - WQ $samplesAlias data member line 231 (as well as $samples data member
    just above it). Each entry in samplesAlias is itself a map of kvps.
  - I put a copy of some of the pertinent PHP code at bottom of file.
  - We handle these differently, using api2hp_mult_sample_resolve function and
    subsequently there is a specific block of logic in the into_hp_row as well.

Below, lists of API field names are listed in *decreasing* order of precedence.
'''
mappings_one_to_many = [
  {'hp':'8 mL SST Collected', 'api': ['sampleStatus2SST8','sampleStatus1SS08', 'sampleStatus1SST8']},
  {'hp':'8 mL SST Collection Date', 'api':['sampleStatus2SST8Time','sampleStatus1SS08Time', 'sampleStatus1SST8Time']}, 
  {'hp':'8 mL PST Collected', 'api': ['sampleStatus2PST8','sampleStatus1PS08', 'sampleStatus1PST8']},
  {'hp':'8 mL PST Collection Date', 'api':['sampleStatus2PST8Time','sampleStatus1PS08Time', 'sampleStatus1PST8Time']}, 
  {'hp':'Saliva Collected', 'api': ['sampleStatus1SAL2', 'sampleStatus1SAL']},
  {'hp':'Saliva Collection Date', 'api':['sampleStatus1SAL2Time', 'sampleStatus1SALTime']} 
]

def api2hp_mult_sample_resolve(api_row, status_fields, time_fields):
  '''
  There are six HP fields that do not have 1-1 mappings:
    - '8 mL SST Collected'
    - '8 mL PST Collected'
    - 'Saliva Collected'
    ... along w/ their associated time-related fields.
  Use this function to determine the values of one of these 
  status/time pair of HP fields.
  Arguments:
    - api_row: the full row of data from API for this participant
    - status_fields: this is a list of API status fields
    - time_Fields: a list of time fields that should be in an order
      that is the 'same'as status_fields -- that is, they should
      correlate.
  Returns:
    - A list with two values: a status and a time, both strings.  
      We do all final conversions here in this function so returned
      values should be in HP format.
  '''
  # We look for value of "RECEIVED" to determine where to stop.
  # See also: api2hp_received function above.
  for i, field in enumerate(status_fields):
    if api_row.get(field, '') == 'RECEIVED':
      #return ['1', api_row[time_fields[i]]]
      #return ['1', api2hp_datetime(api_row[time_fields[i]])]
      return ['1', api2hp_datetime(api_row.get(time_fields[i], ''))]
  return ['0', ''] 


#------------------------------------------------------------------------------
# Consent Cohort field

def determine_consent_cohort(api_row):
    '''
    API                     HP WQ UI                      HP WQ CSV
    --------------------------------------------------------------------
    consentCohort           Consent Cohort                Consent Cohort
      COHORT_1                  Cohort 1                      Cohort 1
      COHORT_2                  Cohort 2                      Cohort 2
      COHORT_3                  Cohort 3                      Cohort 3
      UNSET

    (For COHORT_2:)
    cohort2PilotFlag
      COHORT_2_PILOT            Cohort 2 Pilot                Cohort 2 Pilot
      UNSET
    '''
    ht = {'COHORT_1':'Cohort 1',
          'COHORT_2':'Cohort 2',
          'COHORT_3':'Cohort 3',
        }
    consentCohort = api_row.get('consentCohort', '')
    cohort2PilotFlag = api_row.get('cohort2PilotFlag', '')
    if consentCohort == 'COHORT_2' and cohort2PilotFlag == 'COHORT_2_PILOT':
        return 'Cohort 2 Pilot'
    else:
        return ht.get(consentCohort, '')


#------------------------------------------------------------------------------
# driver

def into_hp_row(api_row):
  '''
  If a value is missig in api_row, using empty string (e.g., address2).
  '''
  out = {}
  # First, handle one-to-one mappings (which are most of them).
  for mapping in mappings_one_to_one:
    api_val = api_row.get(mapping['api'], '')
    hp_val = ''
    if mapping.get('func', '*') != '*':
      hp_val = str2func(mapping['func'])(api_val)
    else:
      hp_val = api_val
    out[mapping['hp']] = hp_val

  # Then, handle one-to-many items.
  # Note: we're handling two at a time -- the value and time
  # need to be processed as a pair (time field depends on value field we 
  # choose.)
  i = 0
  while i < len(mappings_one_to_many):
    hp_val = ''
    status, time = api2hp_mult_sample_resolve(
                        api_row,
                        mappings_one_to_many[i]['api'], # list of status field names
                        mappings_one_to_many[i + 1]['api']) # list of time field names
    out[mappings_one_to_many[i]['hp']] = status
    out[mappings_one_to_many[i + 1]['hp']] = time
    i += 2
  
  # Sal order
  sal_order_status_col_name = 'Saliva Sample Order Status'
  if api_row.get('sampleOrderStatus1SAL2', '*') not in ('*', 'UNSET'):
    out[sal_order_status_col_name] = api_row['sampleOrderStatus1SAL2']
  else:
    out[sal_order_status_col_name] = api_row.get('sampleOrderStatus1SAL','')

  # "Consent Cohort" field
  out['Consent Cohort'] = determine_consent_cohort(api_row)

  #done
  return out

#------------------------------------------------------------------------------
'''

Notes
=====

## Pertinent HealthPro code modules

Field names for data coming from API (ParticipantSummary resource):
  https://github.com/all-of-us/raw-data-repository#participantsummary-api

WorkQueueController class (abbrev as WQC):
  - https://github.com/all-of-us/healthpro/blob/develop/src/Pmi/Controller/WorkQueueController.php)
  - exportAction method handles generating columns and values for the CSV.

WorkQueue class (abbrev as WQ):
  https://github.com/all-of-us/healthpro/blob/develop/src/Pmi/WorkQueue/WorkQueue.php

CodeBook:
  https://github.com/all-of-us/healthpro/blob/develop/src/Pmi/Drc/CodeBook.php


## One-to-many mappings

### WorkQueue class -- samples and samplesAlias data members

    public static $samples = [
        '1SST8' => '8 mL SST',
        '1PST8' => '8 mL PST',
        '1HEP4' => '4 mL Na-Hep',
        '1ED02' => '2 mL EDTA',
        '1ED04' => '4 mL EDTA',
        '1ED10' => '1st 10 mL EDTA',
        '2ED10' => '2nd 10 mL EDTA',
        '1CFD9' => 'Cell-Free DNA',
        '1PXR2' => 'Paxgene RNA',
        '1UR10' => 'Urine 10 mL',
        '1UR90' => 'Urine 90 mL',
        '1SAL' => 'Saliva'
    ];
    public static $samplesAlias = [
        [
            '1SST8' => '1SS08',
            '1PST8' => '1PS08'
        ],
        [
            '1SST8' => '2SST8',
            '1PST8' => '2PST8'
        ],
        [
            '1SAL' => '1SAL2'
        ]
    ];

### WorkQueueController pertinent logic pertaining to 1-to-many mappings.

  foreach (array_keys(WorkQueue::$samples) as $sample) {
      $newSample = $sample;
      foreach (WorkQueue::$samplesAlias as $sampleAlias) {
          if (array_key_exists($sample, $sampleAlias) && $participant->{"sampleStatus" . $sampleAlias[$sample]} == 'RECEIVED') {
              $newSample = $sampleAlias[$sample];
              break;
          }
      }
      $row[] = $participant->{"sampleStatus{$newSample}"} == 'RECEIVED' ? '1' : '0';
      $row[] = WorkQueue::dateFromString($participant->{"sampleStatus{$newSample}Time"}, $app->getUserTimezone(), false);
  }


### Consent Cohort

From https://github.com/all-of-us/healthpro/blob/develop/src/Pmi/WorkQueue/WorkQueue.php --

        'consentCohort' => [
            'label' => 'Consent Cohort',
            'options' => [
                'Cohort 1' => 'COHORT_1',
                'Cohort 2' => 'COHORT_2',
                'Cohort 2 Pilot' => 'COHORT_2_PILOT',
                'Cohort 3' => 'COHORT_3'
            ]
        ],

From WorkQueueController.php line 528:

            $row[] = $participant->consentCohortText;

From Participant.php --

        private static $consentCohortValues = [
                'COHORT_1' => 'Cohort 1',
                'COHORT_2' => 'Cohort 2',
                'COHORT_2_PILOT' => 'Cohort 2 Pilot',
                'COHORT_3' => 'Cohort 3'
            ];
    
...and later in the file...:

        private function getConsentCohortText($participant)
        {
            if ($participant->consentCohort === 'COHORT_2' && isset($participant->cohort2PilotFlag) && $participant->cohort2PilotFlag === 'COHORT_2_PILOT') {
                return self::$consentCohortValues[$participant->cohort2PilotFlag];
            } else {
                return self::$consentCohortValues[$participant->consentCohort] ?? $participant->consentCohort;
            }
        }
}



'''
#------------------------------------------------------------------------------

