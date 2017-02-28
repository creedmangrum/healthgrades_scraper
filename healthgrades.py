import requests
import pprint
import ipdb
import csv
import json
import time
import sys

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

specialties = [
	# {
	# 	'what': 'Orthopaedics',
	# 	'searchType': 'SpecialtyVertical'
	# },
	# {
	# 	'what': 'Orthopedic Surgery',
	# 	'searchType': 'Practicing Specialty'
	# },
	# {
	# 	'what': 'Pulmonology',
	# 	'searchType': 'Practicing Specialty'
	# },
	{
		'what': 'Obstetrics & Gynecology',
		'searchType': 'Practicing Specialty'
	}
]

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

	survey_scores = {}

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
		locations_provider_json = json.loads(locations_provider)


		# I don't think you are going to get enough of these for it to be worth spending the time to parse it out
		# If I'm wrong I can do it, otherwise I'm just providing all the data.
		malpractices = profile_provider_json.get('malpractices')
		sanctions = profile_provider_json.get('sanctions')

		age = profile_provider_json.get('age')
		degree = profile_provider_json.get('degree')
		healthgrades_id = profile_provider_json.get('id')
		languages = profile_provider_json.get('languages')
		locations = [location.get('Name') for location in locations_provider_json]
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
			'locations': locations,
			'malpractices': malpractices,
			'medicare': medicare,
			'sactions': sanctions,
			'med_school': med_school,
			'med_school_year': med_school_year,
			'patient_experience_surveys': patient_experience_surveys,
			'residency': residency,
			'residency_year': residency_year,
			'specialties': specialties,
			'zip_code': str(zip_code) if len(str(zip_code)) == 5 else '0' + str(zip_code)
		}

		info_dict.update(survey_scores)

		return info_dict

	except ValueError as e:
		ipdb.set_trace()
		print e
		return info_dict.update(survey_scores)

	except TypeError as e:
		print e
		ipdb.set_trace()

	except:

		print("Unexpected error:", sys.exc_info()[0])
		return info_dict.update(survey_scores)


for specialty in specialties:
	search_params['what'] = specialty.get('what')
	search_params['searchType'] = specialty.get('searchType')
	what_we_want[specialty.get('what')] = []
	total_count = 1
	search_page = 1
	while len(what_we_want[specialty.get('what')]) < 10:
		start = time.time()

		search_params['pageNum'] = search_page

		r = requests.get(base_url, params=search_params)

		result = r.json()
		search = result.get('search')
		search_results = search.get('searchResults')
		total_count = search_results.get('totalCount')
		providers = search_results.get('provider')
		provider_list = providers.get('results')

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

			what_we_want[specialty.get('what')].append(doc_dict)

		end = time.time()
		print search_page
		print (end - start)
		print (str(len(what_we_want[specialty.get('what')])) + '/' + str(total_count))
		search_page += 1




with open('doc.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(what_we_want[what_we_want.keys()[0]][0].keys())
	for spec, doctors in what_we_want.iteritems():
		for doctor in doctors:
			writer.writerow(doctor.values())



ipdb.set_trace()
