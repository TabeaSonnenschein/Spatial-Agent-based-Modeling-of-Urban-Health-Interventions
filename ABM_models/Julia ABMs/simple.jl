using Agents
using DataFrames
using GeoDataFrames
using Dates
#using PMML
using Random
using Statistics
using Query
using LightGBM
using HTTP
using LibGEOS: LineString
using CSV
using Feather
using CoordinateTransformations
using Proj: Transformation
using ArchGDAL

# Define path_data
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
modelrunname="intervention_scenario"

# Synthetic Population
println("Reading Population Data")
nb_humans = 400
pop_df = CSV.read(path_data * "Population/Agent_pop_clean.csv", DataFrame)
random_subset = pop_df[rand(1:size(pop_df, 1), nb_humans), :]
CSV.write(path_data * "Population/Amsterdam_population_subset.csv", random_subset, writeheader=true)

# Coordinate Reference System and CRS transformers
crs = "epsg:28992"
project_to_WSG84 = Transformation(crs, "epsg:4326")
projecy_to_crs = Transformation("epsg:4326", crs)


 # Load the spatial built environment
buildings = ArchGDAL.read(path_data * "Built Environment/Buildings/Buildings.shp")
streets = ArchGDAL.read(path_data * "Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp")
greenspace = ArchGDAL.read(path_data * "Built Environment/Green Spaces/Green Spaces_RDNew_window.shp")
Residences = ArchGDAL.read(path_data * "Built Environment/Buildings/ResidencesAmsterdamNeighbCode.shp")
Schools = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_schools_RDNew.shp")
Supermarkets = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp")
Universities = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_universities_RDNew.shp")
Kindergardens = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp")
Restaurants = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_Foursquarevenues_Food_RDNew.shp")
Entertainment = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp")
ShopsnServ = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp")
Nightlife = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp")
Profess = ArchGDAL.read(path_data * "Built Environment/Facilities/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp")
spatial_extent = ArchGDAL.read(path_data * "SpatialExtent/Amsterdam Diemen Oude Amstel Extent.shp")
EnvBehavDeterminants = ArchGDAL.read(path_data * "Built Environment/Transport Infrastructure/ModalChoice_determ_200.shp")

# Read the Environmental Stressor Data and Model
AirPollGrid = ArchGDAL.read(path_data * "Air Pollution Determinants/AirPollDeterm_grid50.shp")

 # Load Weather data and set initial weather conditions
monthly_weather_df = DataFrame(CSV.File(path_data * "Weather/monthlyWeather2019TempDiff.csv"))

# Start OSRM Servers
println("Starting OSRM Servers")
run(`C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/start_OSRM_Servers.bat`)

# Read the Mode of Transport Choice Model
println("Reading Mode of Transport Choice Model")
#ModalChoiceModel = load(PMMLTreeClassifier, path_data * "ModalChoiceModel/modalChoice.pmml")

@agent Residents OSMAgent begin
    # socio-demographic attributes
    unique_id::Int
    Neighborhood::String
    current_edu::String
    IndModalPreds::Vector{Int}
    ScheduleID::Int
    MondaySchedule::Vector{Int}
    TuesdaySchedule::Vector{Int}
    WednesdaySchedule::Vector{Int}
    ThursdaySchedule::Vector{Int}
    FridaySchedule::Vector{Int}
    SaturdaySchedule::Vector{Int}
    SundaySchedule::Vector{Int}
    former_activity::Int
    activity::String

    # regular destinations
    Residence::NTuple{2, Float64}
    University::NTuple{2, Float64}
    School::NTuple{2, Float64}
    Workplace::NTuple{2, Float64}

    # mobility behavior variables
    path_memory::Int
    traveldecision::Int
    thishourmode::Vector{String}
    modalchoice::String
    arrival_time::DateTime
    track_duration::Float64
    trip_distance::Float64
    nexthoursmodes::Vector{String}
end

function initialize(nb_humans, path_data, crs="epsg:28992";
    starting_date=DateTime(2019, 1, 1, 6, 50, 0),
    steps_minute=10)
    # Define the global variables   
    properties = Dict(
        :starting_datetime => starting_date,
        :steps_minute => Dates.Minute(steps_minute),
        :current_datetime => starting_date,
        :minute => Dates.minute(current_datetime),
        :weekday => Dates.dayofweek(current_datetime),
        :hour => Dates.hour(current_datetime),
        :temperature => monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Temperature][1]
        :winddirection => monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Winddirection][1]
        :windspeed => monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Windspeed][1]
        :rain => monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :Rain][1]
        :tempdifference => monthly_weather_df[monthly_weather_df[:, :month] .== Dates.month(current_datetime), :TempDifference][1]
    )
    
    # Add other data loading and initialization steps as necessary

    space = GridSpaceSingle((20,20), periodic = false)
    model = UnremovableABM(Humans, space; properties = properties, scheduler = Schedulers.randomly)

    # Create the agent population
    println("Creating Agents")
    println(now())
    for i in 1:nb_humans
        # Generate agent attributes and create the agent
        agent = Residents(Vector(random_subset[i]))
        add_agent_pos!(human, model)
    end
    println(now())
