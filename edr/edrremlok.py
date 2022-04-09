import re
from edri18n import _

class EDRRemlokHelmet(object):  
    LUT = {
        "MicroResource_of:#content=$circuitboard_name": [_("Used in {} blueprints").format(28), _("Exchange value: {} [{}]").format(5, "circuits")],
        "MicroResource_of:#content=$circuitswitch_name": [_("Used in {} blueprints").format(3), _("Exchange value: {} [{}]").format(2, "circuits")],
        "MicroResource_of:#content=$electricalfuse_name": [_("Used in {} blueprints").format(7), _("Exchange value: {} [{}]").format(3, "circuits")],
        "MicroResource_of:#content=$electricalwiring_name": [_("Used in {} blueprints").format(12), _("Exchange value: {} [{}]").format(5, "circuits")],
        "MicroResource_of:#content=$electromagnet_name": [_("Used in {} blueprints").format(23), _("Exchange value: {} [{}]").format(5, "circuits")],
        "MicroResource_of:#content=$ionbattery_name": [_("Used in {} blueprints").format(13), _("Exchange value: {} [{}]").format(5, "circuits")],
        "MicroResource_of:#content=$metalcoil_name": [_("Used in {} blueprints").format(22), _("Exchange value: {} [{}]").format(5, "circuits")],
        "MicroResource_of:#content=$microsupercap_name": [_("Used in {} upgrades").format(7), _("Exchange value: {} [{}]").format(3, "circuits")],
        "MicroResource_of:#content=$microtransformer_name": [_("Used in {} upgrades").format(9), _("Exchange value: {} [{}]").format(4, "circuits")],
        "MicroResource_of:#content=$microelectrode_name": [_("Used in {} upgrades").format(28), _("Exchange value: {} [{}]").format(8, "circuits")],
        "MicroResource_of:#content=$motor_name": [_("Used in {} blueprints").format(7), _("Exchange value: {} [{}]").format(3, "circuits")],
        "MicroResource_of:#content=$opticalfibre_name": [_("Used in {} blueprints").format(11), _("Used in {} upgrades").format(12), _("Exchange value: {} [{}]").format(6, "circuits")],
        
        
        "MicroResource_of:#content=$aerogel_name": [_("Used in {} upgrades").format(4), _("Exchange value: {} [{}]").format(5, "chemicals")],
        "MicroResource_of:#content=$chemicalcatalyst_name": [_("Used in {} blueprints").format(11), _("Exchange value: {} [{}]").format(4, "chemicals")],
        "MicroResource_of:#content=$chemicalsuperbase_name": [_("Used in {} upgrades").format(16), _("Exchange value: {} [{}]").format(5, "chemicals")],
        "MicroResource_of:#content=$epinephrine_name": [_("Used in {} blueprints").format(6), _("Exchange value: {} [{}]").format(3, "chemicals")],
        "MicroResource_of:#content=$epoxyadhesive_name": [_("Used in {} blueprints").format(6), _("Exchange value: {} [{}]").format(3, "chemicals")],
        "MicroResource_of:#content=$graphene_name": [_("Used in {} upgrades").format(12), _("Exchange value: {} [{}]").format(12, "chemicals")],
        "MicroResource_of:#content=$oxygenicbacteria_name": [_("Used in {} blueprints").format(6), _("Exchange value: {} [{}]").format(3, "chemicals")],
        "MicroResource_of:#content=$phneutraliser_name": [_("Used in {} blueprints").format(6), _("Exchange value: {} [{}]").format(3, "chemicals")],
        "MicroResource_of:#content=$rdx_name": [_("Used in {} blueprints").format(12), _("Exchange value: {} [{}]").format(4, "chemicals")],
        "MicroResource_of:#content=$viscoelasticpolymer_name": [_("Used in {} blueprints").format(40), _("Exchange value: {} [{}]").format(6, "chemicals")],
        
        "MicroResource_of:#content=$memorychip_name": [_("Used in {} blueprints").format(3), _("Exchange value: {} [{}]").format(2, "tech")],
        "MicroResource_of:#content=$encryptedmemorychip_name": [_("Used in {} blueprints").format(11), _("Exchange value: {} [{}]").format(2, "tech")],
        "MicroResource_of:#content=$memorychip_name": [_("Used in {} blueprints").format(3), _("Exchange value: {} [{}]").format(2, "tech")],
        "MicroResource_of:#content=$microhydraulics_name": [_("Used in {} blueprints").format(25), _("Exchange value: {} [{}]").format(4, "tech")],
        "MicroResource_of:#content=$microthrusters_name": [_("Used in {} blueprints").format(6), _("Exchange value: {} [{}]").format(3, "tech")],
        "MicroResource_of:#content=$opticallens_name": [_("Used in {} blueprints").format(20), _("Exchange value: {} [{}]").format(5, "tech")],
        "MicroResource_of:#content=$scrambler_name": [_("Used in {} blueprints").format(14), _("Exchange value: {} [{}]").format(3, "tech")],
        "MicroResource_of:#content=$titaniumplating_name": [_("Used in {} blueprints").format(3), _("Used in {} upgrades").format(4), _("Exchange value: {} [{}]").format(6, "tech")],
        "MicroResource_of:#content=$transmitter_name": [_("Used in {} blueprints").format(14), _("Exchange value: {} [{}]").format(3, "tech")],
        "MicroResource_of:#content=$tungstencarbide_name": [_("Used in {} blueprints").format(11), _("Used in {} upgrades").format(16), _("Exchange value: {} [{}]").format(6, "tech")],
        "MicroResource_of:#content=$weaponcomponent_name": [_("Used in {} blueprints").format(33), _("Used in {} upgrades").format(16), _("Exchange value: {} [{}]").format(9, "tech")],

        "MicroResource_of:#content=$manufacturinginstructions_name": [_("Used in {} blueprints").format(56), _("Required by engineer Rosa Dayette to refer Yi Shen [Colonia]"), _("[Data]")],
        "MicroResource_of:#content=$operationalmanual_name": [_("Used in {} blueprints").format(33), _("[Data]")],
        "MicroResource_of:#content=$combattrainingmaterial_name": [_("Used in {} blueprints").format(25), _("[Data]")],
        "MicroResource_of:#content=$combatantperformance_name": [_("Used in {} blueprints").format(25), _("[Data]")],
        "MicroResource_of:#content=$mininganalytics_name": [_("Used in {} blueprints").format(22), _("[Data]")],
        "MicroResource_of:#content=$biometricdata_name": [_("Used in {} blueprints").format(18), _("[Data]")],
        "MicroResource_of:#content=$weapontestdata_name": [_("Used in {} blueprints").format(18), _("[Data]")],
        "MicroResource_of:#content=$spectralanalysisdata_name": [_("Used in {} blueprints").format(17), _("[Data]")],
        "MicroResource_of:#content=$digitaldesigns_name": [_("Used in {} blueprints").format(14), _("Required by engineer Eleanor Bresa to refer Yi Shen [Colonia]"), _("[Data]")],
        "MicroResource_of:#content=$patrolroutes_name": [_("Used in {} blueprints").format(14), _("[Data]")],
        "MicroResource_of:#content=$productionreports_name": [_("Used in {} blueprints").format(14), _("[Data]")],
        "MicroResource_of:#content=$riskassessments_name": [_("Used in {} blueprints").format(14), _("[Data]")],
        "MicroResource_of:#content=$atmosphericdata_name": [_("Used in {} blueprints").format(11), _("[Data]")],
        "MicroResource_of:#content=$audiologs_name": [_("Used in {} blueprints").format(11), _("[Data]")],
        "MicroResource_of:#content=$productionschedule_name": [_("Used in {} blueprints").format(11), _("[Data]")],
        "MicroResource_of:#content=$securityexpenses_name": [_("Used in {} blueprints").format(11), _("[Data]")],
        "MicroResource_of:#content=$topographicalsurveys_name": [_("Used in {} blueprints").format(10), _("[Data]")],
        "MicroResource_of:#content=$reactoroutputreview_name": [_("Used in {} blueprints").format(9), _("[Data]")],
        "MicroResource_of:#content=$ballisticsdata_name": [_("Used in {} blueprints").format(7), _("[Data]")],
        "MicroResource_of:#content=$radioactivitydata_name": [_("Used in {} blueprints").format(6), _("[Data]")],
        "MicroResource_of:#content=$stellaractivitylogs_name": [_("Used in {} blueprints").format(6), _("[Data]")],
        "MicroResource_of:#content=$weaponinventory_name": [_("Used in {} blueprints").format(6), _("[Data]")],
        "MicroResource_of:#content=$bloodtestresults_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$chemicalexperimentdata_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$chemicalformulae_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$chemicalpatents_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$extractionyielddata_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$geneticresearch_name": [_("Used in {} blueprints").format(4), _("Required by Oden Geiger"), _("[Data]")],
        "MicroResource_of:#content=$medicalrecords_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$mineralsurvey_name": [_("Used in {} blueprints").format(4), _("[Data]")],
        "MicroResource_of:#content=$airqualityreports_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$chemicalinventory_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$clinicaltrialrecords_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$evacuationprotocols_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$genesequencingdata_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$maintenancelogs_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$nocdata_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$pharmaceuticalpatents_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$recyclinglogs_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$settlementassaultplans_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$surveilleancelogs_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$tacticalplans_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$troopdeploymentrecords_name": [_("Used in {} blueprints").format(3), _("[Data]")],
        "MicroResource_of:#content=$catmedia_name": [_("Required by Wellington Beck"), _("[Data]")],
        "MicroResource_of:#content=$classicentertainment_name": [_("Required by Wellington Beck"), _("[Data]")],
        "MicroResource_of:#content=$employeegeneticdata_name": [_("Required by Oden Geiger"), _("[Data]")],
        "MicroResource_of:#content=$financialprojections_name": [_("Required by Terra Velasquez to refer Oden Geiger"), _("[Data]")],
        "MicroResource_of:#content=$multimediaentertainment_name": [_("Required by Wellington Beck"), _("[Data]")],
        "MicroResource_of:#content=$opinionpolls_name": [_("Required by Kit Fowler"), _("[Data]")],
        "MicroResource_of:#content=$settlementdefenceplans_name": [_("Required by Hero Ferrari to refer Wellington Beck"), _("[Data]")],
        "MicroResource_of:#content=$smearcampaignplans_name": [_("Required by Yarden Bond"), _("[Data]")],
        "MicroResource_of:#content=$cocktailrecipes_name": [_("Require by engineer Rosa Dayette [Colonia]"), _("[Data]")],
        "MicroResource_of:#content=$culinaryrecipes_name": [_("Required by engineer Rosa Dayette [Colonia]"), _("[Data]")],
        "MicroResource_of:#content=$factionassociates_name": [_("Required by engineer Baltanos to refer Yi Shen [Colonia]"), _("[Data]")],
        "MicroResource_of:#content=$accidentlogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$axcombatlogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$biologicalweapondata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$blacklistdata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$campaignplans_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$censusdata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$chemicalweapondata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$conflicthistory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$criminalrecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$cropyieldanalysis_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$dutyrota_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$employeedirectory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$employeeexpenses_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$employmenthistory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$enhancedinterrogationrecordings_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$espionagematerial_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$explorationjournals_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$factiondonatorlist_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$factionnews_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$fleetregistry_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$geologicaldata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$hydroponicdata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$incidentlogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$influenceprojections_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$internalcorrespondence_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$interrogationrecordings_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$interviewrecordings_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$jobapplications_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$kompromat_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$literaryfiction_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$meetingminutes_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$networkaccesshistory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$networksecurityprotocols_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$nextofkinrecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$patienthistory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$payrollinformation_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$personallogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$photoalbums_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$plantgrowthcharts_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$politicalaffiliations_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$prisonerlogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$propaganda_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$purchaserecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$purchaserequests_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$residentialdirectory_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$salesrecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$seedgeneaology_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$shareholderinformation_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$slushfundlogs_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$spyware_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$taxrecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$travelpermits_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$unionmembership_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$vaccinationrecords_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$vaccineresearch_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$vipsecuritydetail_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$virologydata_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$virus_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$visitorregister_name": [_("Useless"), _("[Data]")],
        "MicroResource_of:#content=$xenodefenceprotocols_name": [_("Useless"), _("[Data]")],
        
        "MicroResource_of:#content=$geneticsample_name": [_("Required by engineer Oden Geiger"), _("[Items]")],
        "MicroResource_of:#content=$biologicalsample_name": [_("Required by engineer Oden Geiger"), _("[Items]")], # artificial name, same as above
        "MicroResource_of:#content=$compressionliquefiedgas_name": [_("Used in {} upgrades").format(16), _("[Items]")],
        "MicroResource_of:#content=$gmeds_name": [_("Used in {} blueprints").format(3), _("[Items]")],
        "MicroResource_of:#content=$geneticrepairmeds_name": [_("Required by engineer Jude Navarro to refer Tera Velasquez"), _("[Items]")],
        "MicroResource_of:#content=$healthmonitor_name": [_("Used in {} upgrades").format(12), _("[Items]")],
        "MicroResource_of:#content=$insightentertainmentsuite_name": [_("Required by engineer Wellington Beck to refer Uma Laszlo"), _("[Items]")],
        "MicroResource_of:#content=$ionisedgas_name": [_("Used in {} upgrades").format(28), _("[Items]")],
        "MicroResource_of:#content=$largecapacitypowerregulator_name": [_("Used in {} upgrades").format(12), _("[Items]")],
        "MicroResource_of:#content=$push_name": [_("Required by engineer Domino Green to refer Kit Fowler"), _("[Items]")],
        "MicroResource_of:#content=$suitschematic_name": [_("Used in {} upgrades").format(12), _("[Items]")],
        "MicroResource_of:#content=$surveillanceequipment_name": [_("Used in {} blueprints").format(3), _("Required by engineer Kit Fowler to refer Yarden Bond"), _("[Items]")],
        "MicroResource_of:#content=$weaponschematic_name": [_("Used in {} upgrades").format(44), _("[Items]")],
        "MicroResource_of:#content=$agriculturalprocesssample_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$biochemicalagent_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$buildingschematic_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$californium_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$castfossil_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$chemicalsample_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$chemicalprocesssample_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$compactlibrary_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$deepmantlesample_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$degradedpowerregulator_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$hush_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$inertiacanister_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$infinity_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$inorganiccontaminant_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$insight_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$insightdatabank_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$lazarus_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$microbialinhibitor_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$mutageniccatalyst_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$nutritionalconcentrate_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$personalcomputer_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$personaldocuments_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$petrifiedfossil_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$pyrolyticcatalyst_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$refinementprocesssample_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$shipschematic_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$syntheticgenome_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$syntheticpathogen_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$universaltranslator_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$trueformfossil_name": [_("Useless"), _("[Items]")],
        "MicroResource_of:#content=$vehicleschematic_name": [_("Useless"), _("[Items]")],

        "MicroResource_of:#content=$salvagedalloys_name": [_("Used in {} blueprints").format(57), _("Used in {} experimental effects").format(2), _("Very common (Alloys)")],
        "MicroResource_of:#content=$galvanisingalloys_name": [_("Used in {} blueprints").format(7), _("Used in {} experimental effects").format(7), _("Common (Alloys)")],
        "MicroResource_of:#content=$phasealloys_name": [_("Used in {} blueprints").format(33), _("Used in {} synthesis").format(5), _("Used in {} experimental effects").format(3), _("Used in 1 tech broker item"), _("Standard (Alloys)")],
        "MicroResource_of:#content=$protolightalloys_name": [_("Used in {} blueprints").format(51), _("Used in {} experimental effects").format(9), _("Rare (Alloys)")],
        "MicroResource_of:#content=$protoradiolicalloys_name": [_("Used in {} blueprints").format(26), _("Used in {} synthesis").format(1), _("Used in 1 tech broker item"), _("Very rare (Alloys)")],

        "MicroResource_of:#content=$gridresistors_name": [_("Used in {} blueprints").format(8), _("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(6), _("Very common (Capacitors)")],
        "MicroResource_of:#content=$hybridcapacitors_name": [_("Used in {} blueprints").format(17), _("Used in {} experimental effects").format(9), _("Common (Capacitors)")],
        "MicroResource_of:#content=$electrochemicalarrays_name": [_("Used in {} blueprints").format(32), _("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(2), _("Used in 1 tech broker item"), _("Standard (Capacitors)")],
        "MicroResource_of:#content=$polymercapacitors_name": [_("Used in {} blueprints").format(19), _("Used in {} experimental effects").format(2), _("Rare (Capacitors)")],
        "MicroResource_of:#content=$militarysupercapacitors_name": [_("Used in {} blueprints").format(13), _("Very rare (Capacitors)")],

        "MicroResource_of:#content=$chemicalstorageunits_name": [_("Used in {} experimental effects").format(6), _("Very common (Chemical)")],
        "MicroResource_of:#content=$chemicalprocessors_name": [_("Used in {} blueprints").format(3), _("Used in 1 tech broker item"), _("Common (Chemical)")],
        "MicroResource_of:#content=$chemicaldistillery_name": [_("Used in {} blueprints").format(2), _("Used in 1 experimental effect"), _("Standard (Chemical)")],
        "MicroResource_of:#content=$chemicalmanipulators_name": [_("Used in {} blueprints").format(4), _("Used in 1 experimental effects"), _("Used in 1 tech broker item"), _("Rare (Chemical)")],
        "MicroResource_of:#content=$pharmaceuticalisolators_name": [_("Used in 1 blueprint"), _("Very rare (Chemical)")],

        "MicroResource_of:#content=$compactcomposites_name": [_("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(6), _("Very common (Composite)")],
        "MicroResource_of:#content=$filamentcomposites_name": [_("Used in {} synthesis").format(4), _("Used in {} experimental effects").format(3), _("Common (Composite)")],
        "MicroResource_of:#content=$highdensitycomposites_name": [_("Used in {} blueprints").format(58), _("Used in {} experimental effects").format(6), _("Standard (Composite)")],
        "MicroResource_of:#content=$proprietarycomposites_name": [_("Used in {} blueprints").format(34), _("Used in {} experimental effects").format(3), _("Rare (Composite)")],
        "MicroResource_of:#content=$coredynamicscomposites_name": [_("Used in {} blueprints").format(21), _("Very rare (Composite)")],

        "MicroResource_of:#content=$basicconductors_name": [_("Used in {} synthesis").format(3), _("Very common (Conductive)")],
        "MicroResource_of:#content=$conductivecomponents_name": [_("Used in {} blueprints").format(62), _("Used in {} experimental effects").format(2), _("Common (Conductive)")],
        "MicroResource_of:#content=$conductiveceramics_name": [_("Used in {} blueprints").format(71), _("Used in 1 experimental effect"), _("Used in 1 tech broker item"), _("Standard (Conductive)")],
        "MicroResource_of:#content=$conductivepolymers_name": [_("Used in {} blueprints").format(22), _("Used in {} experimental effects").format(6), _("Rare (Conductive)")],
        "MicroResource_of:#content=$biotechconductors_name": [_("Used in {} blueprints").format(14), _("Very rare (Conductive)")],

        "MicroResource_of:#content=$crystalshards_name": [_("Used in {} synthesis").format(3), _("Used in 1 experimental effect"), _("Very common (Crystals)")],
        "MicroResource_of:#content=$flawedfocuscrystals_name": [_("Used in {} blueprints").format(8), _("Used in {} experimental effects").format(11), _("Common (Crystals)")],
        "MicroResource_of:#content=$focuscrystals_name": [_("Used in {} blueprints").format(27), _("Used in {} synthesis").format(6), _("Used in {} experimental effects").format(4), _("Used in {} tech broker items").format(2), _("Standard (Crystals)")],
        "MicroResource_of:#content=$refinedfocuscrystals_name": [_("Used in {} blueprints").format(14), _("Used in {} experimental effects").format(4), _("Rare (Crystals)")],
        "MicroResource_of:#content=$exquisitefocuscrystals_name": [_("Used in {} blueprints").format(4), _("Very rare (Crystals)")],

        "MicroResource_of:#content=$guardianpowercell_name": [_("Used in {} synthesis").format(7), _("Used in {} tech broker items").format(9), _("Very common (Guardian)")],
        "MicroResource_of:#content=$guardianpowerconduit_name": [_("Used in {} synthesis").format(5), _("Used in {} tech broker items").format(9), _("Common (Guardian)")],
        "MicroResource_of:#content=$guardiansentinelweaponparts_name": [_("Used in {} synthesis").format(3), _("Used in {} tech broker items").format(10), _("Standard (Guardian)")],
        "MicroResource_of:#content=$guardiantechnologycomponent_name": [_("Used in {} synthesis").format(4), _("Used in {} experimental effects").format(14), _("Very common (Guardian)")],
        "MicroResource_of:#content=$guardianwreckagecomponents_name": [_("Used in {} synthesis").format(3), _("Used in {} tech broker items").format(8), _("Standard (Guardian)")],

        "MicroResource_of:#content=$heatconductionwiring_name": [_("Used in {} blueprints").format(8), _("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(6), _("Very common (Heat)")],
        "MicroResource_of:#content=$heatdispersionplate_name": [_("Used in {} blueprints").format(23), _("Used in {} synthesis").format(4), _("Used in {} experimental effects").format(5), _("Common (Heat)")],
        "MicroResource_of:#content=$heatexchangers_name": [_("Used in {} blueprints").format(13), _("Used in {} synthesis").format(4), _("Used in {} experimental effects").format(3), _("Standard (Heat)")],
        "MicroResource_of:#content=$heatvanes_name": [_("Used in {} blueprints").format(11), _("Used in {} experimental effects").format(5), _("Rare (Heat)")],
        "MicroResource_of:#content=$protoheatradiators_name": [_("Used in {} blueprints").format(10), _("Used in {} synthesis").format(1), _("Very rare (Heat)")],

        "MicroResource_of:#content=$mechanicalscrap_name": [_("Used in {} blueprints").format(61), _("Used in {} experimental effects").format(9), _("Used in 1 tech broker items"), _("Very common (Mechanical)")],
        "MicroResource_of:#content=$mechanicalequipment_name": [_("Used in {} blueprints").format(27), _("Used in {} experimental effects").format(5), _("Common (Mechanical)")],
        "MicroResource_of:#content=$mechanicalcomponents_name": [_("Used in {} blueprints").format(27), _("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(4), _("Used in 1 tech broker item"), _("Standard (Mechanical)")],
        "MicroResource_of:#content=$configurablecomponents_name": [_("Used in {} blueprints").format(19), _("Used in {} experimental effects").format(7), _("Used in 1 tech broker item"), _("Rare (Mechanical)")],
        "MicroResource_of:#content=$improvisedcomponents_name": [_("Used in 1 blueprint"), _("Very rare (Mechanical)")],

        "MicroResource_of:#content=$wornshieldemitters_name": [_("Used in {} blueprints").format(17), _("Used in {} experimental effects").format(9), _("Very common (Shielding)")],
        "MicroResource_of:#content=$shieldemitters_name": [_("Used in {} blueprints").format(87), _("Used in {} experimental effects").format(2), _("Common (Shielding)")],
        "MicroResource_of:#content=$shieldingsensors_name": [_("Used in {} blueprints").format(21), _("Used in {} experimental effects").format(3), _("Standard (Shielding)")],
        "MicroResource_of:#content=$compoundshielding_name": [_("Used in {} blueprints").format(21), _("Used in {} experimental effects").format(1), _("Rare (Shielding)")],
        "MicroResource_of:#content=$imperialshielding_name": [_("Used in {} blueprints").format(3), _("Very rare (Shielding)")],
        
        "MicroResource_of:#content=$thargoidcarapace_name": [_("Used in 1 synthesis"), _("Common (Thargoid)")],
        "MicroResource_of:#content=$thargoidenergycell_name": [_("Used in 1 tech broker item"), _("Standard (Thargoid)")],
        "MicroResource_of:#content=$biomechanicalconduits_name": [_("Used in {} synthesis").format(4), _("Standard (Thargoid)")],
        "MicroResource_of:#content=$thargoidtechnologicalcomponents_name": [_("Used in {} experimental effects").format(2), _("Rare (Thargoid)")],
        "MicroResource_of:#content=$thargoidorganiccircuitry_name": [_("Used in 1 synthesis"), _("Used in 1 tech broker item"), _("Very Rare (Thargoid)")],
        "MicroResource_of:#content=$propulsionelements_name": [_("Used in {} synthesis").format(6), _("Very rare (Thargoid)")],
        "MicroResource_of:#content=$sensorfragment_name": [_("Used in {} synthesis").format(3), _("Required by engineer Professor Palin"), _("Very rare (Thargoid)")],

        "MicroResource_of:#content=$temperedalloys_name": [_("Used in {} experimental effects").format(3), _("Very common (Thermic)")],
        "MicroResource_of:#content=$heatresistantceramics_name": [_("Used in 1 synthesis"), _("Used in {} experimental effects").format(7), _("Used in 1 tech broker item"), _("Common (Thermic)")],
        "MicroResource_of:#content=$precipitatedalloys_name": [_("Used in {} blueprints").format(20), _("Used in {} experimental effects").format(2), _("Standard (Thermic)")],
        "MicroResource_of:#content=$thermicalloys_name": [_("Used in {} blueprints").format(18), _("Used in {} synthesis").format(2), _("Used in 1 experimental effect"), _("Rare (Thermic)")],
        "MicroResource_of:#content=$militarygradealloys_name": [_("Used in {} blueprints").format(3), _("Very rare (Thermic)")],

        
        "MicroResource_of:#content=$carbon_name": [_("Used in {} blueprints").format(48), _("Used in {} synthesis").format(11), _("Used in {} experimental effects").format(3), _("Used for {} tech broker items").format(4), _("Very common (Group 1)")],
        "MicroResource_of:#content=$vanadium_name": [_("Used in {} blueprints").format(47), _("Used in {} synthesis").format(12), _("Used in {} experimental effects").format(5), _("Used for {} tech broker items").format(9), _("Common (Group 1)")],
        "MicroResource_of:#content=$niobium_name": [_("Used in {} blueprints").format(27), _("Used in {} synthesis").format(3), _("Used in {} experimental effects").format(4), _("Used for 1 tech broker item"), _("Stanndard (Group 1)")],
        "MicroResource_of:#content=$ytrium_name": [_("Used in 1 blueprint"), _("Used in {} synthesis").format(2), _("Used in 1 experimental effect"), _("Rare (Group 1)")],
        
        "MicroResource_of:#content=$phosphorus_name": [_("Used in {} blueprints").format(44), _("Used in {} synthesis").format(19), _("Used in {} experimental effects").format(8), _("Used for 1 tech broker item"), _("Very common (Group 2)")],
        "MicroResource_of:#content=$chromium_name": [_("Used in {} blueprints").format(18), _("Used in {} synthesis").format(6), _("Used in {} experimental effects").format(6), _("Used for {} tech broker items").format(4), _("Common (Group 2)")],
        "MicroResource_of:#content=$molybdenum_name": [_("Used in {} blueprints").format(54), _("Used in {} synthesis").format(6), _("Used in {} experimental effects").format(3), _("Used for {} tech broker items").format(3), _("Standard (Group 2)")],
        "MicroResource_of:#content=$technetium_name": [_("Used in {} blueprints").format(33), _("Used in {} synthesis").format(3), _("Used for {} tech broker items").format(9), _("Rare (Group 2)")],
        
        "MicroResource_of:#content=$sulphur_name": [_("Used in {} blueprints").format(46), _("Used in {} synthesis").format(19), _("Used in {} experimental effects").format(3), _("Very common (Group 3)")],
        "MicroResource_of:#content=$manganese_name": [_("Used in {} blueprints").format(57), _("Used in {} synthesis").format(8), _("Used in {} experimental effects").format(2), _("Used in 1 experimental effect"), _("Common (Group 3)")],
        "MicroResource_of:#content=$cadmium_name": [_("Used in {} blueprints").format(13), _("Used in {} synthesis").format(2), _("Used in {} experimental effects").format(2), _("Standard (Group 3)")],
        "MicroResource_of:#content=$ruthenium_name": [_("Used in {} blueprints").format(4), _("Used in {} synthesis").format(1), _("Used in {} experimental effects").format(2), _("Rare (Group 3)")],

        "MicroResource_of:#content=$iron_name": [_("Used in {} blueprints").format(38), _("Used in {} synthesis").format(16), _("Used in {} experimental effects").format(3), _("Very common (Group 4)")],
        "MicroResource_of:#content=$zinc_name": [_("Used in {} blueprints").format(34), _("Used in {} synthesis").format(9), _("Used in {} experimental effects").format(2), _("Common (Group 4)")],
        "MicroResource_of:#content=$tin_name": [_("Used in {} blueprints").format(18), _("Used in {} synthesis").format(4), _("Used in {} experimental effects").format(1), _("Standard (Group 4)")],
        "MicroResource_of:#content=$selenium_name": [_("Used in {} blueprints").format(16), _("Used in {} synthesis").format(5), _("Used in {} experimental effects").format(3), _("Rare (Group 4)")],
        
        "MicroResource_of:#content=$nickel_name": [_("Used in {} blueprints").format(123), _("Used in {} synthesis").format(15), _("Used in 1 experimental effect"), _("Very common (Group 5)")],
        "MicroResource_of:#content=$germanium_name": [_("Used in {} blueprints").format(30), _("Used in {} synthesis").format(3), _("Used in 1 experimental effect"), _("Used for {} tech broker items").format(3), _("Common (Group 5)")],
        "MicroResource_of:#content=$tungsten_name": [_("Used in {} blueprints").format(74), _("Used in {} synthesis").format(13), _("Used in {} experimental effects").format(3), _("Used for {} tech broker items").format(10), _("Standard (Group 5)")],
        "MicroResource_of:#content=$tellurium_name": [_("Used in {} blueprints").format(3), _("Used in {} synthesis").format(2), _("Used for 1 tech broker item"), _("Rare (Group 5)")],

        "MicroResource_of:#content=$rhenium_name": [_("Used for {} tech broker items").format(11), _("Very common (Group 6)")],
        "MicroResource_of:#content=$arsenic_name": [_("Used in {} blueprints").format(6), _("Used in {} synthesis").format(10), _("Used in 1 experimental effect"), _("Used for {} tech broker items").format(3), _("Common (Group 6)")],
        "MicroResource_of:#content=$mercury_name": [_("Used in {} blueprints").format(4), _("Used in {} synthesis").format(10), _("Used in {} experimental effects").format(2), _("Standard (Group 6)")],
        "MicroResource_of:#content=$polonium_name": [_("Used in {} synthesis").format(3), _("Used in 1 experimental effect"), _("Rare (Group 6)")],

        "MicroResource_of:#content=$lead_name": [_("Used in {} synthesis").format(6), _("Very common (Group 7)")],
        "MicroResource_of:#content=$zirconium_name": [_("Used in {} blueprints").format(9), _("Used in {} synthesis").format(10), _("Used in {} experimental effect").format(5), _("Common (Group 7)")],
        "MicroResource_of:#content=$bordon_name": [_("Used in {} synthesis").format(3), _("Standard (Group 7)")],
        "MicroResource_of:#content=$antimony_name": [_("Used in 1 blueprint"), _("Used in {} synthesis").format(2), _("Rare (Group 7)")],
        

        "MicroResource_of:#content=$healthpack_name": [_("TODO: healthpack; some useful info about it")],
        "MicroResource_of:#content=$amm_grenade_shield_name": [_("TODO: grenade shield; some useful info about it")],
       
        "Interactive_Console_APU_Name": [_("TODO: Interactive_Console_APU_Name; some useful info about it")],
        "interactive_rechargepoint_name": [_("TODO: Recharge point; some useful info about it")],        
        "Interactive_Panel_LifeSupport_Cutting01_Name": [_("TODO: panel life support cutting01; some useful info about it")],
        "interactive_lifesupport_door_name": [_("TODO: life support door; some useful info about it")],
        "Interactive_Container_Item_Name": [_("TODO: container item; some useful info about it")],
        "Interactive_Locker_Name": [_("TODO: locker; some useful info about it")],
        "Interactive_GrenadeContainer_Name": [_("TODO: Grenade container; some useful info about it")],
        "Interactive_MedKitContainer_Name": [_("TODO: Medkit container; some useful info about it")],
        "Interactive_Dropbox_Reactor_Name": [_("TODO: Dropbox reactor; some useful info about it")],
        "Interactive_EnergyContainer_Name": [_("TODO: Energy container; some useful info about it")],
        "interactive_suitcharge_name": [_("That's useful to recharge your space suit batteries. [PLACEHOLDER]")],
        "Interactive_DataPort_Generic_Name": [_("Download/upload data from here. [PLACEHOLDER]")],
        "Interactive_AmmoCache_Small_01_Name": [_("TODO: Ammunition Small 01")],
        "interactive_mil_lockera1_1x1_maglock_name": [_("TODO: mil locker a1_1x1 maglock")],
        "interactive_panel_small_cutting01_name": [_("A small panel which can be cut. [PLACEHOLDER]")],
        "Interactive_IndustDropbox_Name": [_("TODO: Interactive_IndustDropbox_Name; some useful info about it")],
        "Interactive_Console_IndustDropbox_Name": [_("TODO: Console industdropbox; some useful info about it")],
        "Interactive_Console_Autho_Name": [_("TODO: Console authorization; some useful info about it")],
        "Interactive_Console_Alarms_Name": [_("TODO: Console alarms; some useful info about it")],
        "Interactive_DataPort_Industrial_Name": [_("TODO: Dapaport industrial; some useful info about it")],
        "Interactive_Locker_Industrial_Name": [_("TODO: Locker industrial; some useful info about it")],
        "Interactive_Console_PDefence_Name": [_("TODO: Console PDefence; some useful info about it")],
        "interactive_rechargepoint2_name": [_("TODO: rechargepoint2; some useful info about it")],
        "Interactive_Console_APTurret_Name": [_("TODO: Console AP Turret; some useful info about it")],
        "interactive_panel_turret_cutting01_name": [_("TODO: panel turret cutting01; some useful info about it")],
        
        "GUI_Interactive_Terminal_Gen_Name": [_("That's a terminal. You can access stuff from it. [PLACEHOLDER]")],
        "GUI_Interactive_ShipyardTerminal_Standing_Gen_01_Name": [_("That's a shipyard terminal. You can manage your ships from there. [PLACEHOLDER]")],
        
        "Humanoid_Corridor_RoomName": [_("TODO: Corridor room")],
        "Humanoid_PowerPlant_RoomName": [_("TODO: Powerplant room")],
        "Humanoid_Bar_RoomName": [_("TODO: Bar room")],
        "Humanoid_Foyer_RoomName": [_("TODO: Foyer room")],
        "Humanoid_Habitat_BLDLongName": [_("TODO: Habitat building")],
        "Humanoid_Cabin_RoomName": [_("TODO: Cabin room")],
        "Humanoid_Leisure_BLDLongName": [_("TODO: Leisure Building")],
        "Humanoid_PowerCentre_BLDLongName": [_("TODO: Power building")],
        "Humanoid_Accessway_A_BLDLongName": [_("TODO: Accessway A building")],
        "Humanoid_Production_Ind_BLDLongName": [_("TODO: Industrial Production building")],
        "Humanoid_Processing_RoomName": [_("TODO: Processing room")],
        
        "MicroResource_of:#content=$energycell_name": [_("Energy cell. [TODO]")],
        
        "skimmerdrone_name":  [_("That's a skimmer drone, yep. [PLACEHOLDER]")],
        
        "higen_authorisationpanel_name": [_("Moultipass? [PLACEHOLDER]")],
        "higen_keypad_name": [_("That's a higen keypad. [PLACEHOLDER]")],
        
        "ps_airlock_6mstr_02_name": [_("That's an airlock 6mstr 02. [PLACEHOLDER]")],
        "ps_turretbasemedium_6m_name": [_("That's a 6m medium turret. [PLACEHOLDER]")],
        "ps_turretbasesmall_3m_name": [_("That's a 3m small turret. [PLACEHOLDER]")],
        "ps_doorway_wide_lux_01_name": [_("That's a wide luxury door 01. [PLACEHOLDER]")],
        "ps_doorway_wide_01_name": [_("That's a wide door 01. [PLACEHOLDER]")],
        "ps_doorway_wide_gen_01_name": [_("That's a wide door gen 01. [PLACEHOLDER]")],
        
        "poi_turretplatforma_name": [_("That's a turret platform. [PLACEHOLDER]")],
    }

    # TODO add synonym lut like it exists in edrinventory, to facilitate user lookups

    def __init__(self):
        self.unknown_things = []

    def describe_target(self, pointing_event):
        emote_regex = r"^\$HumanoidEmote_TargetMessage:#player=\$cmdr_decorate:#name=(.+);:#targetedAction=\$HumanoidEmote_point_Action_Targeted;:#target=\$(.+);( [0-9]+)?[;]+$"
        m = re.match(emote_regex, pointing_event.get("Message", ""))
        target = None
        if m:
            target = m.group(2)
    
        if target is None:
            print(pointing_event)
            print("no target")
            return None
        target = target.rstrip(";")
        return self.describe_item(target)

    def describe_item(self, item):
        if item in EDRRemlokHelmet.LUT:
            return EDRRemlokHelmet.LUT[item]

        print(item)
        c_item = item.strip(" -_").lower()
        c_item = c_item.rstrip(";")
        if c_item.startswith("$"):
            c_item = c_item[1:]
        if c_item.endswith("_name"):
            c_item = c_item[:-5]
        print(c_item)
        adj_item = "MicroResource_of:#content=${}_name".format(c_item)
        print(adj_item)
        if adj_item in EDRRemlokHelmet.LUT:
            return EDRRemlokHelmet.LUT[adj_item]

        if item not in self.unknown_things:
            self.unknown_things.append(item)
            print(self.unknown_things)
        return None # [_("Unknown"), item]