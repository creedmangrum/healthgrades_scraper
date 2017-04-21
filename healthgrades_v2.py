import requests
import pprint
import ipdb
import csv
import json
import os
import time
import sys

from constants import specialties, specialties_to_search

what_we_want = {}

base_url = (
	'https://www.healthgrades.com/api3/usearch'
)

other_params = {
	'isFirstRequest': True,
	'sort.provider': 'bestmatch',
	'sort.practice': 'bestmatch',
	'entityCode': None,
	'requestId': None,
	'sessionId': None
}

search_params = {
	'category': 'all',
	'distances': 'National',
	'pageNum': 1,
	'pageSize.practice': 8,
	'pageSize.provider': 100,
	'searchType': 'SpecialtyVertical',
	'what': 'Orthopaedics',

}

malpractices_list = []
sanctions_list = []
patient_experience_surveys_list = []
malpractices_list_filenames = []
sanctions_list_filenames = []
patient_experience_surveys_list_filenames = []
patient_experience_surveys_list_specialty_filenames = {}

provider_list_filenames = {}
doctor_errors = []


def ensure_dir(file_path):
    		directory = os.path.dirname(file_path)
    		if not os.path.exists(directory):
        		os.makedirs(directory)
    		return file_path


def merge_csvs(filenames, directory, name):
	output_filename = directory + name + '-combined-' + str(time.time()) + '.csv'
	output_file = open(output_filename, 'wb')
	output_writer = csv.writer(output_file)
	for i, filename in enumerate(filenames):
		if name == 'patient_experience':
			filename = 'patient_exp_surveys/' + filename
		with open(filename, 'rU') as f:
			reader = csv.reader(f)
			# if i == 0:
			# 	output_writer.writerow(reader[0])
			# for row in reader[1:]:
			for row in reader:
				output_writer.writerow(row)


def create_malpractices_csv(filename):
	global malpractices_list
	global malpractices_list_filenames
	directory = ensure_dir('{}/'.format('malpractices'))
	with open(directory + filename, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(malpractices_list[0].keys())
		for doctor in malpractices_list:
			try:
				writer.writerow(doctor.values())
			except:
				print('error with: ' + doctor['healthgrades_id'])
				continue
	malpractices_list = []
	malpractices_list_filenames.append(filename)
	print('malpractices csv created')

def create_sanctions_csv(filename):
	global sanctions_list
	global sanctions_list_filenames
	directory = ensure_dir('{}/'.format('sanctions'))
	with open(directory + filename, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(sanctions_list[0].keys())
		for doctor in sanctions_list:
			try:
				writer.writerow(doctor.values())
			except:
				print('error with: ' + doctor['healthgrades_id'])
				continue
	sanctions_list = []
	sanctions_list_filenames.append(filename)
	print('sanctions csv created')

def create_patient_experience_surveys_csv(filename):
	global patient_experience_surveys_list
	global patient_experience_surveys_list_filenames
	directory = ensure_dir('{}/'.format('patient_exp_surveys'))
	with open(directory + filename, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(patient_experience_surveys_list[0].keys())
		for doctor in patient_experience_surveys_list:
			try:
				writer.writerow(doctor.values())
			except:
				print('error with: ' + doctor['healthgrades_id'])
				continue
	patient_experience_surveys_list = []
	patient_experience_surveys_list_filenames.append(filename)


def get_empty_malpractice_dict(malpractice_index):
	return {
		malpractice_index + '-' + "complaint": "",
		malpractice_index + '-' + "formattedDate": "",
		malpractice_index + '-' + "malpracticeType": "",
		malpractice_index + '-' + "rangeOrAmountDisplay": "",
		malpractice_index + '-' + "regionName": "",
		malpractice_index + '-' + "showDate": "",
		malpractice_index + '-' + "closedDate": "",
		malpractice_index + '-'  "rangeOrAmount": "",
		malpractice_index + '-' + "amount": "",
		malpractice_index + '-' + "location": "",
		# malpractice_index + '-' + "location-" + "cityName": "",
		# malpractice_index + '-' + "location-" + "cityAndState": "",
		# malpractice_index + '-' + "location-" + "cityStateZipBestMatch": "",
		# malpractice_index + '-' + "location-" + "providerCount": "",
		# malpractice_index + '-' + "location-" + "region-" + "regionAbbreviation": "",
		# malpractice_index + '-' + "location-" + "region-" + "regionName": "",
		# malpractice_index + '-' + "location-" + "region-" + "cities": "",
		# malpractice_index + '-' + "location-" + "region-" + "cityInitials": "",
		# malpractice_index + '-' + "location-" + "region-" + "isCountry": "",
		# malpractice_index + '-' + "location-" + "region-" + "zip": "",
		# malpractice_index + '-' + "location-" + "region-" + "coordinates-" + "latitude": "",
		# malpractice_index + '-' + "location-" + "region-" + "coordinates-" + "longitude": "",
		# malpractice_index + '-' + "location-" + "region-" + "coordinates-" + "latLon": ""
		# malpractice_index + '-' + "location-" + "region-" + "nation": "",
		# malpractice_index + '-' + "location-" + "region-" + "hasProviders": "",
		# malpractice_index + '-' + "location-" + "region-" + "supressRegionLink": ""          
		# malpractice_index + '-' + "location-" + "locRegion-" + "regionAbbreviation": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "regionName": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "cities": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "cityInitials": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "isCountry": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "zip": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "coordinates-" + "latitude": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "coordinates-" + "longitude": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "coordinates-" + "latLon": ""
		# malpractice_index + '-' + "location-" + "locRegion-" + "nation": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "hasProviders": "",
		# malpractice_index + '-' + "location-" + "locRegion-" + "supressRegionLink": ""
		# malpractice_index + '-' + "location-" + "isNeighborhood": "",
		# malpractice_index + '-' + "location-" + "regionAbbreviation": ""
    }

def get_empty_sanctions_dict(sanctions_index):
	return {
		sanctions_index + '-' + "actionTaken": "",
		sanctions_index + '-' + "category": "",
		sanctions_index + '-' + "description": "",
		sanctions_index + '-' + "formattedDate": "",
		sanctions_index + '-' + "location": "",
		# sanctions_index + '-' + 'location-' + "cityName": "",
		# sanctions_index + '-' + 'location-' + "cityAndState": "New York",
		# sanctions_index + '-' + 'location-' + "cityStateZipBestMatch": "New York",
		# sanctions_index + '-' + 'location-' + "providerCount": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "regionAbbreviation": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "regionName": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "cities": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "cityInitials": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "isCountry": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "zip": "",
		# sanctions_index + '-' + 'location-' + 'region-' + 'coordinates-' + "latitude": "",
		# sanctions_index + '-' + 'location-' + 'region-' + 'coordinates-' + "longitude": "",
		# sanctions_index + '-' + 'location-' + 'region-' + 'coordinates-' + "latLon": ""
		# sanctions_index + '-' + 'location-' + 'region-' + "nation": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "hasProviders": "",
		# sanctions_index + '-' + 'location-' + 'region-' + "supressRegionLink": ""
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "regionAbbreviation": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "regionName": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "cities": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "cityInitials": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "isCountry": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "zip": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + 'coordinates-' + "latitude": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + 'coordinates-' + "longitude": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + 'coordinates-' + "latLon": ""
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "nation": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "hasProviders": "",
		# sanctions_index + '-' + 'location-' + 'locRegion-' + "supressRegionLink": ""
		# sanctions_index + '-' + 'location-' + "isNeighborhood": "",
		# sanctions_index + '-' + 'location-' + "regionAbbreviation": ""
		sanctions_index + '-' + "pdfPath": "",
		sanctions_index + '-' + "recipientName": "",
		sanctions_index + '-' + "regionName": "",
		sanctions_index + '-' + "sanctionDate": "",
		sanctions_index + '-' + "showDate": ""
    }


def get_provider_profile_data(url, doc):
	provider_url = 'https://www.healthgrades.com' + str(url)
	resp = requests.get(provider_url)
	html_string = resp.text

	survey_data_start_string = 'pageState.pes'
	survey_data_start_index = html_string.find(survey_data_start_string)
	survey_data_end_string = 'pageState.facilityLocations'
	survey_data_end_index = html_string.find(survey_data_end_string)

	survey_data_json_with_trailing_garbage = html_string[survey_data_start_index:survey_data_end_index]

	starting_garbage_end_index = len('pageState.pes = ')
	trailing_garbage_start_index = survey_data_json_with_trailing_garbage.find(';\r\n\r\n') 

	try:
		trailing_garbage_start_index = trailing_garbage_start_index if trailing_garbage_start_index > 0 else survey_data_json_with_trailing_garbage.find(';\n\n')
		survey_data_json = json.loads(survey_data_json_with_trailing_garbage[starting_garbage_end_index:trailing_garbage_start_index])
	except:
		survey_data_json = None


	if survey_data_json:
		try:
			survey_aggregates = survey_data_json.get('model', {}).get('insights', {}).get('aggregates', [])
		except:
			survey_aggregates = []
	else:
		survey_aggregates = []

	survey_scores = {
		'Helpfulness Count': '',
		'Helpfulness Score': '',
		'Scheduling Count': '',
		'Scheduling Score': '',
		'Staff Count': '',
		'Staff Score': '',
		'Trustworthiness Count': '',
		'Trustworthiness Score': ''
	}

	if len(survey_aggregates):

		for survey in survey_aggregates:
			survey_scores[str(survey.get('title') + ' Count')] = survey.get('responseCount')
			survey_scores[str(survey.get('title') + ' Score')] = survey.get('actualScore')


	profile_provider_to_the_end = html_string[html_string.find('profile.provider'):]
	profile_provider = profile_provider_to_the_end[len('profile.provider = '):profile_provider_to_the_end.find(';\r\n')]
	profile_provider = profile_provider[:profile_provider.find(';\n\t\t')]

	locations_provider_to_the_end = html_string[html_string.find('pageState.facilityLocations'):]
	locations_provider = locations_provider_to_the_end[len('pageState.facilityLocations = '):locations_provider_to_the_end.find(';\n')]

	info_dict = {}

	try:
		profile_provider_json = json.loads(profile_provider)
		# locations_provider_json = json.loads(locations_provider)


		# I don't think you are going to get enough of these for it to be worth spending the time to parse it out
		# If I'm wrong I can do it, otherwise I'm just providing all the data.
		malpractices = profile_provider_json.get('malpractices')
		sanctions = profile_provider_json.get('sanctions')

		age = profile_provider_json.get('age')
		degree = profile_provider_json.get('degree')
		healthgrades_id = profile_provider_json.get('id')
		languages = profile_provider_json.get('languages')
		# locations = [location.get('Name') for location in locations_provider_json]
		educations = profile_provider_json.get('education')
		med_school_filter = [[education['name'], education['year']] for education in educations if education['educationType'] == 'MEDSCH']
		med_school = med_school_filter[0][0] if len(med_school_filter) else None
		med_school_year = med_school_filter[0][1] if len(med_school_filter) else None
		residency_filter = [[education['name'], education['year']] for education in educations if education['educationType'] == 'RESIDE']
		residency = residency_filter[0][0] if len(residency_filter) else None
		residency_year = residency_filter[0][1] if len(residency_filter) else None
		specialties = [specialty.get('name') for specialty in profile_provider_json.get('specialties')]
		zip_code = profile_provider_json.get('primaryPractice', {}).get('offices', [])[0].get('address', {}).get('location', {}).get('region', {}).get('zip')

		affiliated_hospitals = profile_provider_json.get('affiliatedHospitals')

		affiliated_hospital_dict = {}
		if affiliated_hospitals:
			for i, hospital in enumerate(affiliated_hospitals):
				affiliated_hospital_dict['affiliated_hospital_' + str(i) + '_name'] = hospital.get('name')
				affiliated_hospital_dict['affiliated_hospital_' + str(i) + '_teaching'] = hospital.get('isTeachingHospital')


		fellowship_filter = [{'name': education['name'], 'year': education['year']} for education in educations if education['educationType'] == 'FELLOW']
		fellow_dict = {}
		if fellowship_filter:
			for i, fellowship in enumerate(fellowship_filter):
				fellow_dict['fellow_' + str(i) + '_name'] = fellowship['name']
				fellow_dict['fellow_' + str(i) + '_year'] = fellowship['year']

		insurances = len(profile_provider_json.get('insuranceAccepted'))
		medicare = False
		if len(profile_provider_json.get('insuranceAccepted')):
			for insurance in profile_provider_json.get('insuranceAccepted'):
				if insurance.get('code') == 'MEDICA':
					medicare = True

		# Need to break this up to be more userful. Need to validate that all questions are the same across providers
		# FOr now I'll just provide it all
		patient_experience_surveys = profile_provider_json.get('patientExperienceSurveys')


		info_dict = {
			'affiliated_hospital_1_name': affiliated_hospital_dict.get('affiliated_hospital_1_name'),
			'affiliated_hospital_1_teaching': affiliated_hospital_dict.get('affiliated_hospital_1_teaching'),
			'affiliated_hospital_2_name': affiliated_hospital_dict.get('affiliated_hospital_2_name'),
			'affiliated_hospital_2_teaching': affiliated_hospital_dict.get('affiliated_hospital_2_teaching'),
			'affiliated_hospital_3_name': affiliated_hospital_dict.get('affiliated_hospital_3_name'),
			'affiliated_hospital_3_teaching': affiliated_hospital_dict.get('affiliated_hospital_3_teaching'),
			'age': age,
			'degree': degree,
			'healthgrades_id': healthgrades_id,
			'fellow_1_name': fellow_dict.get('fellow_1_name'),
			'fellow_1_year': fellow_dict.get('fellow_1_year'),
			'fellow_2_name': fellow_dict.get('fellow_2_name'),
			'fellow_2_year': fellow_dict.get('fellow_2_year'),
			'fellow_3_name': fellow_dict.get('fellow_3_name'),
			'fellow_3_year': fellow_dict.get('fellow_3_year'),
			'insurances': insurances,
			'languages': languages,
			'medicare': medicare,
			'med_school': med_school,
			'med_school_year': med_school_year,
			'patient_experience_surveys': patient_experience_surveys,
			'residency': residency,
			'residency_year': residency_year,
			'specialties': specialties,
			'zip_code': str(zip_code) if len(str(zip_code)) == 5 else '0' + str(zip_code)
		}

		if malpractices:
			global malpractices_list
			malpractices_dict = {}
			for i in range(10):
				malpractices_dict.update(get_empty_malpractice_dict(str(i + 1)))
			for i, malpractice in enumerate(malpractices):
				for key, value in malpractice.iteritems():
					malpractices_dict[str(i) + '-' + key] = value if value else ''
			to_append = malpractices_dict.copy()
			to_append.update({
				'healthgrades_id': healthgrades_id,
			})
			malpractices_list.append(to_append)

		if sanctions:
			global sanctions_list
			sanctions_dict = {}
			for i in range(10):
				sanctions_dict.update(get_empty_sanctions_dict(str(i + 1)))
			for i, sanction in enumerate(sanctions):
				for key, value in sanction.iteritems():
					sanctions_dict[str(i) + '-' + key] = value if value else ''
			to_append = sanctions_dict.copy()
			to_append.update({
				'healthgrades_id': healthgrades_id,
			})
			sanctions_list.append(to_append)

		if patient_experience_surveys:
			global patient_experience_surveys_list
			experience_surveys = {
				'223-count': '',
				'223-providerScorePercent': '',
				'223-nationalScore': '',
				'223-providerScoreRoundedPercent': '',
				'223-nationalScorePercent': '',
				'223-question': '',
				'223-providerScore': '',
				'223-resultsSortOrder': '',
				'223-roundedProviderScoreDescription': '',
				'223-comparisonText': '',
				'223-roundedNationalScoreDescription': '',
				'223-nationalScoreRoundedPercent': '',
				'224-count': '',
				'224-providerScorePercent': '',
				'224-nationalScore': '',
				'224-providerScoreRoundedPercent': '',
				'224-nationalScorePercent': '',
				'224-question': '',
				'224-providerScore': '',
				'224-resultsSortOrder': '',
				'224-roundedProviderScoreDescription': '',
				'224-comparisonText': '',
				'224-roundedNationalScoreDescription': '',
				'224-nationalScoreRoundedPercent': '',
				'225-count': '',
				'225-providerScorePercent': '',
				'225-nationalScore': '',
				'225-providerScoreRoundedPercent': '',
				'225-nationalScorePercent': '',
				'225-question': '',
				'225-providerScore': '',
				'225-resultsSortOrder': '',
				'225-roundedProviderScoreDescription': '',
				'225-comparisonText': '',
				'225-roundedNationalScoreDescription': '',
				'225-nationalScoreRoundedPercent': '',
				'226-count': '',
				'226-providerScorePercent': '',
				'226-nationalScore': '',
				'226-providerScoreRoundedPercent': '',
				'226-nationalScorePercent': '',
				'226-question': '',
				'226-providerScore': '',
				'226-resultsSortOrder': '',
				'226-roundedProviderScoreDescription': '',
				'226-comparisonText': '',
				'226-roundedNationalScoreDescription': '',
				'226-nationalScoreRoundedPercent': '',
				'227-count': '',
				'227-providerScorePercent': '',
				'227-nationalScore': '',
				'227-providerScoreRoundedPercent': '',
				'227-nationalScorePercent': '',
				'227-question': '',
				'227-providerScore': '',
				'227-resultsSortOrder': '',
				'227-roundedProviderScoreDescription': '',
				'227-comparisonText': '',
				'227-roundedNationalScoreDescription': '',
				'227-nationalScoreRoundedPercent': '',
				'228-count': '',
				'228-providerScorePercent': '',
				'228-nationalScore': '',
				'228-providerScoreRoundedPercent': '',
				'228-nationalScorePercent': '',
				'228-question': '',
				'228-providerScore': '',
				'228-resultsSortOrder': '',
				'228-roundedProviderScoreDescription': '',
				'228-comparisonText': '',
				'228-roundedNationalScoreDescription': '',
				'228-nationalScoreRoundedPercent': '',
				'229-count': '',
				'229-providerScorePercent': '',
				'229-nationalScore': '',
				'229-providerScoreRoundedPercent': '',
				'229-nationalScorePercent': '',
				'229-question': '',
				'229-providerScore': '',
				'229-resultsSortOrder': '',
				'229-roundedProviderScoreDescription': '',
				'229-comparisonText': '',
				'229-roundedNationalScoreDescription': '',
				'229-nationalScoreRoundedPercent': '',
				'230-count': '',
				'230-providerScorePercent': '',
				'230-nationalScore': '',
				'230-providerScoreRoundedPercent': '',
				'230-nationalScorePercent': '',
				'230-question': '',
				'230-providerScore': '',
				'230-resultsSortOrder': '',
				'230-roundedProviderScoreDescription': '',
				'230-comparisonText': '',
				'230-roundedNationalScoreDescription': '',
				'230-nationalScoreRoundedPercent': '',
				'231-count': '',
				'231-providerScorePercent': '',
				'231-nationalScore': '',
				'231-providerScoreRoundedPercent': '',
				'231-nationalScorePercent': '',
				'231-question': '',
				'231-providerScore': '',
				'231-resultsSortOrder': '',
				'231-roundedProviderScoreDescription': '',
				'231-comparisonText': '',
				'231-roundedNationalScoreDescription': '',
				'231-nationalScoreRoundedPercent': '',
			}
			remaining_survey_items = {}
			experience_surveys_keys = list(experience_surveys.keys())
			question_ids = [key.split('-')[0] for key in experience_surveys_keys]
			questions_ids_set = set()
			for question_id in question_ids:
				questions_ids_set.add(question_id)

			for obj in patient_experience_surveys:
				for key, value in obj.iteritems():
					if str(str(obj['questionID']) + '-' + key) in experience_surveys_keys:
						experience_surveys[str(str(obj['questionID']) + '-' + key)] = value if value else ''
					else:
						remaining_survey_items[str(str(obj['questionID']) + '-' + key)] = value if value else ''

			to_append = experience_surveys.copy()
			to_append.update({
				'healthgrades_id': healthgrades_id,
				'remaining_survey_items': remaining_survey_items,
			})
			patient_experience_surveys_list.append(to_append)


		info_dict.update(survey_scores)

		return info_dict

	except ValueError as e:
		print e
		return info_dict.update(survey_scores)

	except TypeError as e:
		print e
		return info_dict.update(survey_scores)

	except NameError as e:
		print e
		return info_dict.update(survey_scores)

	except:

		print("Unexpected error:", sys.exc_info()[0])
		return info_dict.update(survey_scores)


for specialty in specialties_to_search:
	search_params['what'] = specialty.get('what')
	search_params['searchType'] = specialty.get('searchType')
	what_we_want[specialty.get('what')] = []
	total_count = 1
	search_page = 1
	counter = 0

	# if specialty == 'AAC':
	# 	search_page = 24
	# 	counter = search_page * 100

	while counter < total_count:
		start = time.time()

		search_params['pageNum'] = search_page

		r = requests.get(base_url, params=search_params)

		result = r.json()
		search = result.get('search')
		search_results = search.get('searchResults')
		total_count = search_results.get('totalCount')
		providers = search_results.get('provider')
		provider_list = providers.get('results')
		provider_info_list = []
		for doc in provider_list:
			provider_profile_info = get_provider_profile_data(doc.get('providerUrl'), doc)
			doc_dict = {
				'address': doc.get('address'),
				'name': doc.get('displayName'),
				'gender': doc.get('gender'),
				'specialty': doc.get('specialty'),
				'survey_rating': doc.get('surveyOverallRatingPercent'),
				'survey_count': doc.get('surveyUserCount'),
			}

			if provider_profile_info:
				doc_dict.update(provider_profile_info)
			
			provider_info_list.append(doc_dict)

		directory = ensure_dir('{}/'.format(specialty.get('what')))

		filename =str(directory + 'complete-' + specialty.get('what') + '-' + str(search_page) + '-of' + '-' + str(int(total_count/search_params['pageSize.provider'])) + '-' + str(time.time()) + '.csv')
		with open(filename, 'wb') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(provider_info_list[0].keys())
			for doctor in provider_info_list:
				try:
					writer.writerow(doctor.values())
				except:
					print('error with: ' + doctor['name'])
					doctor_errors.append((doctor['name'], doctor['healthgrades_id']))
					continue
		
		if provider_list_filenames.get(specialty.get('what')):
			provider_list_filenames[specialty.get('what')].append(filename)
		else:
			provider_list_filenames[specialty.get('what')] = [filename]


		if len(patient_experience_surveys_list) > 100:
			more_surveys_filename = str('complete-surveys-'  + str(time.time()) + '.csv')
			if patient_experience_surveys_list_specialty_filenames.get(specialty.get('what')):
				patient_experience_surveys_list_specialty_filenames[specialty.get('what')].append(more_surveys_filename)
			else:
				patient_experience_surveys_list_specialty_filenames[specialty.get('what')] = [more_surveys_filename]
			create_patient_experience_surveys_csv(more_surveys_filename)

		if len(malpractices_list) > 100:

			malpractices_filename = str('complete-malpractices-' + str(time.time()) + '.csv')
			create_malpractices_csv(malpractices_filename)
			

		if len(sanctions_list) > 100:
			sanctions_filename = str('complete-sanctions-' + str(time.time()) + '.csv')
			create_sanctions_csv(sanctions_filename)

		print (filename + ' was created')
		end = time.time()
		print search_page
		print (end - start)
		counter += len(provider_info_list)
		print (str(str(counter) + '/' + str(total_count)))
		search_page += 1

	directory = ensure_dir('{}/'.format(specialty.get('what')))
	merge_csvs(provider_list_filenames[specialty.get('what')], directory, 'info')
	merge_csvs(patient_experience_surveys_list_specialty_filenames[specialty.get('what')], directory, 'patient_experience')


if len(patient_experience_surveys_list) > 0:
	more_surveys_filename = str('complete-surveys-'  + str(time.time()) + '.csv')
	create_patient_experience_surveys_csv(more_surveys_filename)

if len(malpractices_list) > 0:
	malpractices_filename = str('complete-malpractices-' + str(time.time()) + '.csv')
	create_malpractices_csv(malpractices_filename)
	

if len(sanctions_list) > 0:
	sanctions_filename = str('complete-sanctions-' + str(time.time()) + '.csv')
	create_sanctions_csv(sanctions_filename)

pprint.pprint(doctor_errors)

ipdb.set_trace()
