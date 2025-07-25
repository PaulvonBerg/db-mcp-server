# resources/travel_resources.py

import logging
from datetime import datetime
from typing import Any

from config import BASE_URL_STADA, BASE_URL_TIMETABLES
from utils import fetch_from_db_api

# Import MCP instance from shared module
from server_instance import mcp

# --- MCP Resources ---

@mcp.resource("file://reference/station-categories")
async def get_station_categories_guide() -> str:
    """
    Reference guide explaining German railway station categories and their significance.
    """
    return """# German Railway Station Categories (DB StaDa)

Deutsche Bahn classifies all German railway stations into 7 categories based on passenger volume, importance, and services available:

## Category 1: Major International Hubs
- **Examples**: Frankfurt(Main)Hbf, Berlin Hauptbahnhof, München Hauptbahnhof, Hamburg Hauptbahnhof
- **Characteristics**: >50,000 passengers/day, international connections, full service facilities
- **Services**: DB Lounge, travel centers, extensive shopping, restaurants, car rental
- **Accessibility**: Complete barrier-free access, multiple elevators, tactile guidance systems

## Category 2: Major Regional Centers  
- **Examples**: Dresden Hauptbahnhof, Hannover Hauptbahnhof, Stuttgart Hauptbahnhof
- **Characteristics**: 25,000-50,000 passengers/day, major regional hub
- **Services**: Travel center, shops, restaurants, parking facilities
- **Accessibility**: Barrier-free access, elevators to all platforms

## Category 3: Important Regional Stations
- **Examples**: Augsburg Hauptbahnhof, Kiel Hauptbahnhof, Erfurt Hauptbahnhof
- **Characteristics**: 10,000-25,000 passengers/day, regional importance
- **Services**: Ticket machines, basic shops, parking
- **Accessibility**: Most platforms accessible, some elevators

## Category 4: Regional Stations
- **Examples**: Bamberg, Freiburg(Breisgau)Hbf, Rostock Hauptbahnhof
- **Characteristics**: 2,500-10,000 passengers/day
- **Services**: Ticket machines, limited facilities
- **Accessibility**: Selected platforms accessible

## Category 5: Local Transportation Hubs
- **Examples**: Various suburban and town stations
- **Characteristics**: 1,000-2,500 passengers/day
- **Services**: Basic ticket facilities
- **Accessibility**: Limited accessibility features  

## Category 6: Local Stations
- **Examples**: Smaller town and suburban stations
- **Characteristics**: 500-1,000 passengers/day
- **Services**: Basic platform facilities
- **Accessibility**: Often limited accessibility

## Category 7: Small Local Stations
- **Examples**: Rural and small town stations
- **Characteristics**: <500 passengers/day
- **Services**: Minimal facilities, often unstaffed
- **Accessibility**: Basic platform access only

## Usage for Travel Planning:
- **Categories 1-2**: Full services, guaranteed accessibility, ideal for connections
- **Categories 3-4**: Good regional connections, reasonable facilities
- **Categories 5-7**: Basic service, check accessibility needs in advance

This categorization helps travelers understand what services and accessibility features to expect at their departure, connection, or destination stations."""

@mcp.resource("file://reference/train-types")
async def get_train_types_guide() -> str:
    """
    Comprehensive guide to German train types and their characteristics.
    """
    return """# German Train Types Guide

Understanding German train designations helps you choose the right service for your journey:

## High-Speed Trains

### ICE (InterCityExpress) 🚄
- **Speed**: Up to 320 km/h (200 mph)
- **Routes**: Major cities, international connections
- **Features**: WiFi, restaurant car, air conditioning, power outlets
- **Reservations**: Recommended, especially for peak times
- **Examples**: Berlin-Munich, Frankfurt-Paris, Hamburg-Basel

### IC (InterCity) 🚆
- **Speed**: Up to 200 km/h (125 mph)  
- **Routes**: Long-distance connections between major cities
- **Features**: Restaurant/bistro car, air conditioning, WiFi (selected trains)
- **Reservations**: Optional but recommended
- **Examples**: Hamburg-Munich, Berlin-Cologne

## Regional Trains

### RE (RegionalExpress) 🚃
- **Speed**: Up to 160 km/h (100 mph)
- **Routes**: Regional connections, skip smaller stations
- **Features**: Basic comfort, some have WiFi
- **Reservations**: Not possible (unreserved seating)
- **Usage**: Ideal for medium-distance regional travel

### RB (RegionalBahn) 🚂
- **Speed**: Up to 120 km/h (75 mph)
- **Routes**: Local service, stops at all stations
- **Features**: Basic regional train service
- **Reservations**: Not possible
- **Usage**: Local transportation, connecting small towns

## Urban Transit

### S-Bahn (Stadtschnellbahn) Ⓢ
- **Speed**: Up to 120 km/h (75 mph)
- **Routes**: Urban and suburban areas around major cities
- **Features**: Frequent service, integrated with local transport
- **Reservations**: Not applicable
- **Usage**: Commuting, airport connections, city exploration

### U-Bahn (Underground/Subway) Ⓤ
- **Speed**: Up to 80 km/h (50 mph)
- **Routes**: Inner city transportation (Berlin, Hamburg, Munich, Nuremberg)
- **Features**: Underground metro system
- **Reservations**: Not applicable
- **Usage**: City center transportation

## Special Services

### TGV/AVE/Railjet 🌍
- **International high-speed trains**
- **TGV**: To/from France (Paris, Strasbourg, Marseille)
- **AVE**: To/from Spain (Barcelona, Madrid)
- **Railjet**: To/from Austria (Vienna, Salzburg, Innsbruck)

### Night Trains 🌙
- **ÖBB Nightjet**: Overnight services to Austria, Italy, Switzerland
- **Features**: Sleeping cars, couchettes, seated accommodation

## Ticket Integration:
- **ICE/IC**: Require long-distance tickets
- **RE/RB**: Covered by regional tickets and Deutschland-Ticket
- **S-Bahn**: Integrated with local transport tickets
- **Deutschlandticket**: Valid for RE, RB, S-Bahn, but NOT ICE/IC

## Travel Tips:
- **Speed vs. Price**: ICE fastest but most expensive, RE/RB slower but cheaper
- **Connections**: All train types connect seamlessly at major stations
- **Real-time Info**: Use DB Navigator app or station displays for current information"""

@mcp.resource("file://stations/major-hubs")  
async def get_major_station_hubs() -> str:
    """
    List of Germany's most important railway stations (Category 1-2).
    """
    try:
        # Get Category 1 and 2 stations
        category_1_stations = await fetch_from_db_api(f"{BASE_URL_STADA}/stations", params={"category": "1", "limit": 50})
        category_2_stations = await fetch_from_db_api(f"{BASE_URL_STADA}/stations", params={"category": "2", "limit": 100})
        
        result = "# Major German Railway Hubs\n\n"
        result += "These are Germany's most important railway stations, offering full services and excellent connectivity:\n\n"
        
        result += "## Category 1 Stations (International Hubs)\n"
        result += "The most important stations with >50,000 passengers/day:\n\n"
        
        for station in category_1_stations.get("result", [])[:15]:  # Top 15
            city = station.get("mailingAddress", {}).get("city", "Unknown")
            eva = station.get("evaNumbers", [{}])[0].get("number", "N/A") if station.get("evaNumbers") else "N/A"
            result += f"- **{station['name']}** ({city})\n"
            result += f"  - EVA: {eva}\n"
            result += f"  - Services: International connections, DB Lounge, full facilities\n\n"
        
        result += "## Category 2 Stations (Major Regional Centers)\n"
        result += "Important regional hubs with 25,000-50,000 passengers/day:\n\n"
        
        for station in category_2_stations.get("result", [])[:10]:  # Top 10
            city = station.get("mailingAddress", {}).get("city", "Unknown")
            eva = station.get("evaNumbers", [{}])[0].get("number", "N/A") if station.get("evaNumbers") else "N/A"
            result += f"- **{station['name']}** ({city})\n"
            result += f"  - EVA: {eva}\n"
            result += f"  - Services: Regional hub, travel center, good facilities\n\n"
        
        result += "\n## Usage Notes:\n"
        result += "- These stations offer the best connectivity for long-distance travel\n"
        result += "- All have barrier-free access and comprehensive facilities\n"
        result += "- Ideal for major route connections and international travel\n"
        result += "- Most have direct airport or city center connections\n"
        
        return result
        
    except Exception as e:
        return f"# Major German Railway Hubs\n\nError loading station data: {str(e)}\n\nPlease use the station search tools for current information."

@mcp.resource("file://services/accessibility-guide")
async def get_accessibility_guide() -> str:
    """
    Comprehensive guide to accessibility features and services at German railway stations.
    """
    return """# Accessibility Guide for German Railways

Deutsche Bahn is committed to barrier-free travel. Here's your complete guide to accessibility features and services:

## 🚊 Platform Access

### Elevators (Aufzüge)
- **Availability**: All Category 1-2 stations, most Category 3-4 stations
- **Features**: Voice announcements, Braille buttons, spacious for wheelchairs
- **Status Checking**: Use FaSta API tools to check real-time elevator status
- **Alternative**: Ask station staff for platform access alternatives when elevators are down

### Escalators (Rolltreppen)
- **Accessibility**: Not suitable for wheelchairs, useful for mobility-impaired travelers
- **Features**: Handrails, clear step markings
- **Status**: Check via accessibility tools before travel

### Ramps and Level Access
- **Modern Stations**: Most new platforms have level or ramped access
- **Older Stations**: May require elevator or staff assistance

## 🚄 Train Access

### ICE Trains
- **Wheelchair Spaces**: Dedicated spaces in 2nd class, reservable
- **Accessible Toilets**: Available in most ICE trains
- **Boarding**: Level boarding at major stations, mobile ramps available
- **Audio Announcements**: Clear announcements for visually impaired

### IC/EC Trains  
- **Wheelchair Access**: Most trains have accessible cars
- **Reservations**: Wheelchair spaces must be reserved in advance
- **Assistance**: Staff assistance available for boarding

### Regional Trains (RE/RB)
- **Modern Trains**: Low-floor access, wheelchair spaces
- **Older Trains**: May require assistance or have limited accessibility
- **Variation**: Accessibility varies by train age and type

## 🎧 Visual and Hearing Impairments

### Visual Impairment Support
- **Tactile Guidance**: Yellow tactile strips on platforms at major stations
- **Audio Announcements**: Clear platform and train announcements
- **Braille**: Elevator buttons have Braille markings
- **Guide Dogs**: Welcome on all trains and in stations

### Hearing Impairment Support
- **Visual Displays**: LED displays show train information
- **Vibrating Alerts**: Some platforms have vibrating notification systems
- **Sign Language**: Staff at major stations often know basic sign language

## 🎯 Mobility Aid Services

### Wheelchair Users
- **Reservation Required**: Book wheelchair spaces when buying tickets
- **Platform Access**: Use elevators, avoid escalators
- **Train Types**: ICE and IC most accessible, regional trains vary
- **Assistance**: Station staff can provide boarding assistance

### Walking Aids
- **Priority Seating**: Available near train entrances
- **Handrails**: Present in trains and on platforms
- **Rest Areas**: Seating available on platforms at major stations

## 📞 Assistance Services

### Mobility Service Center (MSZ)
- **Phone**: 01806 512 512 (within Germany)
- **Advance Booking**: 24 hours before travel recommended
- **Services**: Boarding assistance, platform guidance, luggage help
- **Coverage**: Available at major stations

### 3-S-Zentrale (Service Centers)
- **Purpose**: 24/7 emergency and assistance hotline
- **Services**: Emergency help, lost property, general assistance
- **Contact**: Available via station information or emergency phones

## 🏢 Station Facilities

### Accessible Toilets
- **Location**: All Category 1-2 stations, most Category 3+ stations
- **Features**: Wheelchair accessible, emergency call buttons
- **Cost**: Usually require small fee (€0.50-1.00)

### Parking
- **Disabled Parking**: Reserved spaces near station entrances
- **Identification**: Disabled parking permit required
- **Booking**: Some stations allow advance parking reservations

### Hotels and Accommodation
- **Station Hotels**: Many major stations have accessible hotel rooms
- **Advance Booking**: Reserve accessible rooms in advance
- **Features**: Roll-in showers, lowered fixtures, wide doorways

## 📱 Digital Accessibility Tools

### DB Navigator App
- **Accessibility**: Screen reader compatible
- **Features**: Voice guidance, large text options
- **Real-time**: Live accessibility status updates

### Accessibility Prompts (This MCP Server)
- **Route Checking**: Use 'accessibility_check' prompt for route planning
- **Real-time Status**: Check elevator/escalator status before travel
- **Station Information**: Get comprehensive accessibility information

## 💡 Travel Tips

### Planning Your Journey
1. **Book Early**: Reserve wheelchair spaces and assistance 24+ hours ahead
2. **Check Status**: Use accessibility tools to check elevator status
3. **Allow Extra Time**: Factor in additional time for assistance
4. **Backup Plans**: Know alternative routes if elevators are down

### During Travel  
- **Arrive Early**: Allow extra time for assistance and platform access
- **Stay Informed**: Check real-time updates via displays or apps
- **Ask for Help**: Station and train staff are trained to assist
- **Emergency**: Use emergency phones/buttons if you need immediate help

### Rights and Support
- **EU Rights**: Strong passenger rights for disabled travelers
- **Compensation**: Available for accessibility service failures
- **Feedback**: Report accessibility issues to improve services
- **Advocacy**: Contact disability advocacy groups for serious issues

## 🚨 Emergency Procedures

### If You're Stranded
1. **Contact 3-S-Zentrale**: 24/7 emergency assistance
2. **Platform Emergency**: Use emergency phones on platforms
3. **Train Emergency**: Notify conductor or use emergency communication
4. **Medical Emergency**: Call 112 (general emergency) or notify DB staff

This guide covers the essentials of accessible rail travel in Germany. For specific questions or to request assistance, contact DB's Mobility Service Center in advance of your journey."""

@mcp.resource("file://status/current-disruptions")
async def get_system_disruptions_overview() -> str:
    """
    System-wide overview of current major disruptions across the German railway network.
    """
    try:
        # Get a sample of major stations to check for widespread disruptions
        major_stations = ["8000105", "8011160", "8000261", "8002549", "8000152", "8000191"]  # Frankfurt, Berlin, Munich, Hamburg, Cologne, Hannover
        station_names = ["Frankfurt Hbf", "Berlin Hbf", "München Hbf", "Hamburg Hbf", "Köln Hbf", "Hannover Hbf"]
        
        result = "# Current System-Wide Disruptions\n\n"
        result += f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        result += "Overview of current disruptions at major German railway hubs:\n\n"
        
        total_disruptions = 0
        for eva, name in zip(major_stations, station_names):
            try:
                changes = await fetch_from_db_api(f"{BASE_URL_TIMETABLES}/fchg/{eva}", accept_xml=True)
                timetable_data = changes.get("timetable", {})
                stops = timetable_data.get("s", [])
                
                if stops:
                    disrupted_trains = len([s for s in stops if s.get("departure", {}).get("@cs") == "c" or s.get("departure", {}).get("@delay")])
                    total_disruptions += disrupted_trains
                    
                    if disrupted_trains > 0:
                        result += f"## {name}\n"
                        result += f"- **Affected Services**: {disrupted_trains} trains with delays/cancellations\n"
                        
                        # Count cancellations vs delays
                        cancellations = len([s for s in stops if s.get("departure", {}).get("@cs") == "c"])
                        delays = disrupted_trains - cancellations
                        
                        if cancellations > 0:
                            result += f"- **Cancellations**: {cancellations} trains cancelled\n"
                        if delays > 0:
                            result += f"- **Delays**: {delays} trains delayed\n"
                        result += "\n"
                    else:
                        result += f"## {name}\n✅ No major disruptions reported\n\n"
                else:
                    result += f"## {name}\n✅ No disruptions reported\n\n"
                    
            except Exception as e:
                result += f"## {name}\n❌ Status unavailable (API error)\n\n"
        
        result += "---\n"
        if total_disruptions > 50:
            result += "⚠️ **HIGH DISRUPTION LEVEL**: Significant delays and cancellations across the network\n"
        elif total_disruptions > 20:
            result += "⚠️ **MODERATE DISRUPTIONS**: Some delays and cancellations affecting services\n"
        elif total_disruptions > 0:
            result += "✅ **MINOR DISRUPTIONS**: Limited impact on services\n"
        else:
            result += "✅ **NORMAL OPERATIONS**: No major disruptions detected\n"
        
        result += "\n## Recommendations:\n"
        result += "- Check specific route disruptions using the 'current_disruptions' prompt\n"
        result += "- Allow extra travel time during high disruption periods\n"
        result += "- Consider alternative routes or departure times\n"
        result += "- Use real-time tools for up-to-date information\n"
        
        return result
        
    except Exception as e:
        return f"# Current System-Wide Disruptions\n\n❌ **Error loading disruption data**: {str(e)}\n\nPlease use individual station disruption tools for current information."