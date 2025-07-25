# prompts/travel_prompts.py
"""
Travel-related MCP prompts for Deutsche Bahn services
"""

# Import MCP instance from shared module
from server_instance import mcp
from tools.station_tools import get_station_by_name, get_stations_by_position
from tools.timetable_tools import get_recent_timetable_changes, get_full_timetable_changes, get_planned_timetable
from tools.parking_tools import get_parking_by_station, get_parking_prognoses
from tools.facility_tools import find_facilities

# --- MCP Prompts ---

@mcp.prompt(
    name="accessibility_check",
    title="Check Route Accessibility & Barrier-Free Travel",
    description="Verify if barrier-free travel is possible between two German railway stations by checking elevator and escalator status. Essential for travelers with mobility aids, wheelchairs, or heavy luggage. Provides real-time facility status and alternative route suggestions."
)
async def accessibility_check_prompt(start_station: str, end_station: str):
    """Check accessibility for travel between two stations"""
    
    # Find station numbers for both stations
    start_station_search = await get_station_by_name(name=start_station, limit=1)
    end_station_search = await get_station_by_name(name=end_station, limit=1)
    
    if not start_station_search or not end_station_search:
        return [{"role": "user", "content": {"type": "text", "text": "Error: One or both stations could not be found."}}]
    
    start_station_number = start_station_search[0].number
    end_station_number = end_station_search[0].number
    
    # Find elevators at both stations
    start_facilities = await find_facilities(station_number=start_station_number, type='ELEVATOR')
    end_facilities = await find_facilities(station_number=end_station_number, type='ELEVATOR')
    
    # Check for inactive elevators
    inactive_start = [f.description for f in start_facilities if f.state == 'INACTIVE']
    inactive_end = [f.description for f in end_facilities if f.state == 'INACTIVE']
    
    # Build the response message
    summary = f"Accessibility Check for Route: {start_station} → {end_station}\\n\\n"
    
    if not inactive_start:
        summary += f"✅ {start_station}: All elevators operational\\n"
    else:
        summary += f"⚠️ {start_station}: {len(inactive_start)} elevator(s) out of service:\\n"
        for elevator in inactive_start:
            summary += f"   • {elevator}\\n"
    
    if not inactive_end:
        summary += f"✅ {end_station}: All elevators operational\\n"
    else:
        summary += f"⚠️ {end_station}: {len(inactive_end)} elevator(s) out of service:\\n"
        for elevator in inactive_end:
            summary += f"   • {elevator}\\n"
    
    summary += "\\n"
    if inactive_start or inactive_end:
        summary += "🚨 **Barrier-free travel may be impacted**\\n"
        summary += "• Check with station staff for alternative access\\n"
        summary += "• Consider requesting assistance via DB Mobility Service\\n"
        summary += "• Allow extra time for alternative routes\\n"
    else:
        summary += "✅ **Barrier-free travel should be possible**\\n"
        summary += "• All elevators at both stations are operational\\n"
        summary += "• Standard accessibility features available\\n"
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="parking_prognosis", 
    title="Parking Availability Forecast at Train Stations",
    description="Get parking space availability predictions for German train stations up to 2 hours in advance. Perfect for Park & Ride planning and avoiding overcrowded parking facilities. Includes predictions for different parking types (garage, outdoor, disabled spaces)."
)
async def parking_prognosis_prompt(station_name: str, datetime: str):
    """Get parking availability forecast for a station"""
    
    # Find station ID
    station_search = await get_station_by_name(name=station_name, limit=1)
    if not station_search or not station_search[0].evaNumbers:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: Station {station_name} could not be found or has no EVA number."}}]
    
    stop_place_id = str(station_search[0].evaNumbers[0].number)
    
    # Find parking facilities
    parking_facilities = await get_parking_by_station(stop_place_id=stop_place_id)
    if not parking_facilities:
        return [{"role": "user", "content": {"type": "text", "text": f"No parking facilities found at {station_name}."}}]
    
    summary = f"Parking Forecast for {station_name} at {datetime}:\\n\\n"
    
    found_prognosis = False
    for facility in parking_facilities:
        if facility.hasPrognosis:
            try:
                prognoses = await get_parking_prognoses(facility_id=facility.id, datetime=datetime)
                if prognoses and len(prognoses) > 0:
                    found_prognosis = True
                    facility_name = facility.name[0]['text'] if facility.name else f"Facility {facility.id}"
                    
                    # Extract prognosis information
                    prognosis = prognoses[0].get('prognosis', {})
                    if 'text' in prognosis:
                        summary += f"🅿️ **{facility_name}**\\n"
                        summary += f"   Forecast: {prognosis['text']}\\n\\n"
            except Exception as e:
                continue
    
    if not found_prognosis:
        summary += "ℹ️ No parking forecasts available for this station at the requested time.\\n"
        summary += "\\n**Available Parking Facilities:**\\n"
        for facility in parking_facilities[:3]:  # Show first 3
            facility_name = facility.name[0]['text'] if facility.name else f"Facility {facility.id}"
            summary += f"• {facility_name}\\n"
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="recent_timetable_changes",
    title="Real-Time Train Delays & Service Disruptions", 
    description="Get the latest train delays, cancellations, and platform changes from the last 2 minutes. Essential for current travel situations and real-time journey adjustments. Shows immediate disruptions affecting your departure station."
)
async def recent_timetable_changes_prompt(station_name: str):
    """Get recent timetable changes for a station"""
    
    station_search = await get_station_by_name(name=station_name, limit=1)
    if not station_search:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: Station {station_name} could not be found in timetable database."}}]
    
    # Get main EVA number from StaDa station
    main_eva = None
    for eva in station_search[0].evaNumbers:
        if eva.isMain:
            main_eva = eva.number
            break
    if not main_eva:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: No EVA number found for {station_name}."}}]
    eva_number = str(main_eva)
    changes = await get_recent_timetable_changes(eva_number=eva_number)
    
    if not changes.get("stops"):
        return [{"role": "user", "content": {"type": "text", "text": f"✅ No recent changes reported for {station_name} in the last 2 minutes."}}]
    
    summary = f"🚨 Recent Changes at {station_name} (Last 2 Minutes):\\n\\n"
    
    for stop in changes["stops"][:10]:  # Limit to 10 most recent
        trip = stop.get('tripLabel', {})
        line = f"{trip.get('category', '')} {trip.get('trip_number', '')}"
        
        if stop.get("departure"):
            event = stop["departure"]
            direction = event.get('planned_path', '').split('|')[-1] if event.get('planned_path') else 'Unknown'
            
            if event.get("changed_status") == "c":
                summary += f"❌ **{line}** to {direction}: CANCELLED\\n"
            elif event.get("delay"):
                delay_min = event.get("delay", 0)
                summary += f"⏰ **{line}** to {direction}: +{delay_min} min delay\\n"
            elif event.get("changed_platform"):
                old_platform = event.get("planned_platform", "?")
                new_platform = event.get("changed_platform", "?")
                summary += f"🚉 **{line}** to {direction}: Platform change {old_platform} → {new_platform}\\n"
    
    summary += "\\n💡 Check departure boards for the most current information."
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="planned_timetable_window",
    title="Train Schedule for Specific Time Window",
    description="Display all trains departing/arriving within a specific time period at a German railway station. Perfect for planning connections, finding the best departure time, or checking available options during your preferred travel window."
)
async def planned_timetable_window_prompt(station_name: str, date: str, start_time: str, end_time: str):
    """Get planned timetable for a specific time window"""
    
    station_search = await get_station_by_name(name=station_name, limit=1)
    if not station_search:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: Station {station_name} could not be found in timetable database."}}]
    
    # Get main EVA number from StaDa station
    main_eva = None
    for eva in station_search[0].evaNumbers:
        if eva.isMain:
            main_eva = eva.number
            break
    if not main_eva:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: No EVA number found for {station_name}."}}]
    eva_number = str(main_eva)
    
    # Get timetable data for the start hour
    start_hour = start_time[:2]
    timetable = await get_planned_timetable(eva_number=eva_number, date=date, hour=start_hour)
    
    if not timetable.get("stops"):
        return [{"role": "user", "content": {"type": "text", "text": f"No scheduled trains found for {station_name} during the specified time window."}}]
    
    summary = f"🚂 Scheduled Trains at {station_name}\\n"
    summary += f"📅 {date} from {start_time} to {end_time}:\\n\\n"
    
    from datetime import datetime
    start_dt = datetime.strptime(date + start_time, "%y%m%d%H%M")
    end_dt = datetime.strptime(date + end_time, "%y%m%d%H%M")
    
    found_trains = False
    for stop in timetable["stops"]:
        event = stop.get("departure", stop.get("arrival"))
        if not event or not event.get("planned_time"):
            continue
            
        event_dt = datetime.strptime(event["planned_time"], "%y%m%d%H%M")
        
        if start_dt <= event_dt <= end_dt:
            found_trains = True
            trip = stop.get('tripLabel', {})
            line = f"{trip.get('category', '')} {trip.get('trip_number', '')}"
            direction = event.get('planned_path', '').split('|')[-1] if event.get('planned_path') else 'Unknown'
            time_str = event["planned_time"][-4:]  # Last 4 chars = HHMM
            platform = event.get('planned_platform', '?')
            
            event_type = "🚂" if "departure" in stop else "🚃"
            summary += f"{event_type} {time_str} - **{line}** to {direction} (Platform {platform})\\n"
    
    if not found_trains:
        summary += "ℹ️ No trains scheduled during this specific time window."
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="station_services",
    title="Complete Station Information & Services",
    description="Get comprehensive information about a German railway station including all available services, facilities, contact details, and amenities. Perfect for trip planning and understanding what's available at your departure or destination station."
)
async def station_services_prompt(station_name: str):
    """Get comprehensive station information"""
    
    # Search for the station
    station_search = await get_station_by_name(name=station_name, limit=1)
    if not station_search:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: Station '{station_name}' could not be found."}}]
    
    station = station_search[0]
    
    # Build comprehensive station information
    summary = f"🏢 **{station.name}** - Complete Station Guide\\n\\n"
    
    # Basic information
    summary += f"📍 **Location:** {station.mailingAddress.city if station.mailingAddress else 'N/A'}\\n"
    summary += f"🏷️ **Category:** {station.category} (1=International Hub ↔ 7=Local Station)\\n"
    
    if station.evaNumbers:
        summary += f"🔢 **EVA Number:** {station.evaNumbers[0].number}\\n"
    
    summary += "\\n"
    
    # Services and facilities
    summary += "🏪 **Services Available:**\\n"
    if hasattr(station, 'hasDBLounge') and station.hasDBLounge:
        summary += "✅ DB Lounge\\n"
    if hasattr(station, 'hasTravelCenter') and station.hasTravelCenter:
        summary += "✅ Travel Center\\n"
    if hasattr(station, 'hasLockerSystem') and station.hasLockerSystem:
        summary += "✅ Luggage Lockers\\n"
    if hasattr(station, 'hasWiFi') and station.hasWiFi:
        summary += "✅ Free WiFi\\n"
    
    # Try to get parking information
    if station.evaNumbers:
        try:
            parking_facilities = await get_parking_by_station(stop_place_id=str(station.evaNumbers[0].number))
            if parking_facilities:
                summary += f"\\n🚗 **Parking:** {len(parking_facilities)} facilities available\\n"
                for facility in parking_facilities[:2]:  # Show first 2
                    facility_name = facility.name[0]['text'] if facility.name else f"Facility {facility.id}"
                    summary += f"   • {facility_name}\\n"
        except:
            pass  # Parking info not critical
    
    # Contact information
    if hasattr(station, 'ril100Identifiers') and station.ril100Identifiers:
        summary += f"\\n📡 **Station Code (RIL100):** {station.ril100Identifiers[0].rilIdentifier}\\n"
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="nearby_stations",
    title="Find Railway Stations Near Location", 
    description="Discover German railway stations within a specified radius of any geographic location. Ideal for finding the closest train station to your hotel, airport, attraction, or current position. Includes distance calculations and station details."
)
async def nearby_stations_prompt(latitude: float, longitude: float, radius: float = 2.0):
    """Find stations near geographic coordinates"""
    
    # Find nearby stations
    nearby_stations = await get_stations_by_position(
        latitude=latitude, 
        longitude=longitude, 
        radius=radius
    )
    
    if not nearby_stations:
        return [{"role": "user", "content": {"type": "text", "text": f"No railway stations found within {radius} km of coordinates ({latitude:.4f}, {longitude:.4f})."}}]
    
    summary = f"🗺️ Railway Stations Near ({latitude:.4f}, {longitude:.4f})\\n"
    summary += f"📏 Search Radius: {radius} km\\n\\n"
    
    for i, station in enumerate(nearby_stations[:8], 1):  # Limit to 8 results
        distance = getattr(station, 'distance_km', 0)
        summary += f"{i}. **{station.name}**\\n"
        summary += f"   📍 Distance: ~{distance:.1f} km\\n"
        summary += f"   🔢 ID: {station.id}\\n"
        summary += f"   📐 Coordinates: {station.lat:.4f}, {station.lon:.4f}\\n\\n"
    
    if len(nearby_stations) > 8:
        summary += f"... and {len(nearby_stations) - 8} more stations in the area."
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]

@mcp.prompt(
    name="current_disruptions",
    title="Comprehensive Service Disruption Overview",
    description="Get a complete overview of current train service disruptions, delays, and cancellations at a station. Combines real-time updates from the last 2 minutes with all known future disruptions. Essential for understanding the current service situation."
)
async def current_disruptions_prompt(station_name: str):
    """Get comprehensive disruption information for a station"""
    
    # Find the station
    station_search = await get_station_by_name(name=station_name, limit=1)
    if not station_search:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: Station '{station_name}' could not be found in timetable database."}}]
    
    # Get main EVA number from StaDa station
    main_eva = None
    for eva in station_search[0].evaNumbers:
        if eva.isMain:
            main_eva = eva.number
            break
    if not main_eva:
        return [{"role": "user", "content": {"type": "text", "text": f"Error: No EVA number found for {station_name}."}}]
    eva_number = str(main_eva)
    
    # Get both recent changes and full changes
    try:
        recent_changes = await get_recent_timetable_changes(eva_number=eva_number)
        full_changes = await get_full_timetable_changes(eva_number=eva_number)
        
        summary = f"📊 Service Status Overview for **{station_name}**\\n\\n"
        
        # Process recent changes (last 2 minutes)
        if recent_changes.get("stops"):
            summary += "🔥 **IMMEDIATE UPDATES** (last 2 minutes):\\n"
            for stop in recent_changes["stops"][:5]:  # Limit to 5 most recent
                trip = stop.get('tripLabel', {})
                line = f"{trip.get('category', '')} {trip.get('trip_number', '')}"
                
                if stop.get("departure"):
                    event = stop["departure"]
                    direction = event.get('planned_path', '').split('|')[-1] if event.get('planned_path') else 'Unknown'
                    if event.get("changed_status") == "c":
                        summary += f"❌ {line} to {direction}: CANCELLED\\n"
                    elif event.get("delay"):
                        delay_min = event.get("delay", 0)
                        summary += f"⏰ {line} to {direction}: +{delay_min} minutes delay\\n"
            summary += "\\n"
        
        # Process full changes  
        if full_changes.get("stops"):
            summary += "📋 **ALL KNOWN DISRUPTIONS:**\\n"
            cancelled_count = 0
            delayed_count = 0
            
            for stop in full_changes["stops"]:
                if stop.get("departure"):
                    event = stop["departure"]
                    if event.get("changed_status") == "c":
                        cancelled_count += 1
                    elif event.get("delay"):
                        delayed_count += 1
            
            summary += f"• {cancelled_count} trains cancelled\\n"
            summary += f"• {delayed_count} trains delayed\\n"
        
        if not recent_changes.get("stops") and not full_changes.get("stops"):
            summary += "✅ **No current disruptions reported** for this station."
        
    except Exception as e:
        summary = f"❌ Error retrieving disruption information: {str(e)}"
    
    return [{"role": "user", "content": {"type": "text", "text": summary}}]