
Pundits = {'Alzheimers':['@Alzheimers','@AlzRegistry'],
	'ArtificialIntelligence':[],
	'Autism':[],
	'Biotechnology':['@adamfeuerstein','@AndyBiotech','@zDonShimoda','@JPZaragoza1'],
	'Cancer':['@mtmdphd','@rsm2800','@TedOkonCOA','@EdwardWinstead'],
	'Climate':['@kate_sheppard','@BillNye','@billmckibben','@KHayhoe','@EricPooley'],
	'ComputerSecurity':['@nortononline','@gcluley','@briankrebs','@jeremiahg','@uscert_gov'],
	'DarkMatter':[],
	'Diabetes':['@johnlapuma','@joybauer','@AndreaChernusRD','@johnlapuma','@DrFrankLipman','@TeamNutrition'],
	'Dinosaurs':['@NatGeoChannel'],
	'EarthQuakes':['@CRepp7News','@mikebettes','@hobson_c','@KTVBLarry','@KylesWeather'], #Natural Disaster Experts
	'FossilFuels':['@KylesWeather','@billmckibben','@elaineishere','@hjones_nike','@JigarShahDC','@EarthVitalSigns'],
	'Genetics':['@genevunige'],
	'GlobalWarming':['@kate_sheppard','@BillNye','@billmckibben','@KHayhoe','@EricPooley'],
	'HeartDiseases':['@EricTopol','@CardiologyToday','@CardioNews','@DrLeslieSaxon','@jhfrudd','@cpcannon'],
	'HivAids':['@benyoungmd','@hiv','@TheBodyDotCom'],
	'Hurricanes':['@ericfisher','@mikeseidel','@EverythingWX','@StuOstro','@spann','@afreedma'],
	'Mars':['@NASA','@nasa_astronauts','@Astro_Ron','@neiltyson','@Astro_Mike','@Astro_Nicole','@badastronomer'],
	'Moon':['@NASA','@nasa_astronauts','@Astro_Ron','@neiltyson','@Astro_Mike','@Astro_Nicole','@badastronomer'],
	'Pollution':['@arielhs','@elaineishere','@hjones_nike','@hlovins'],
	'SolarCells':['@SolarPowerWorld','@GreenEnergyNews'],
	'SolarEnergy':['@GreenEnergyNews','@SolarPowerWorld']} 


def find_users(category):
	if Pundits.has_key(category):
		lookup_res = {'return_val': 1,
					'pundit_list' : Pundits[category]}
		return lookup_res
	else: 
		lookup_res = {'return_val': 0,
					'pundit_list' : [0]}
		return lookup_res 

#x = find_users('GlobalWarming')