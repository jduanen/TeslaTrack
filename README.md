# TeslaTrack
Tesla tracker with geofencing and notification

***WIP***

This uses the TeslaPy module and requires OAUTH authentication with the tesla servers.

N.B. The TeslaPy module seems to be built for 'api_version'>=4.x and doesn't work so well with older cars (e.g., 2014 ModelS is currently at 'api_version'=3.6).  The module's behavior with lower api versions is unpredictable (e.g., sometimes it returns data from another of the list of vehicles).

**TODO**
* Fork TeslaPy and make it work for 'api_version'<4.x
* Find an authentication mechanism that runs on linux
* Create web-based interface
* Integrate with maps -- current locations, regions display/define, etc.

**Design Notes**
* key features
  - enumerate all vehicles -- select (proper) subset of them to track
  - report information on current status of selected vehicles
  - refer to vehicles by friendly names -- i.e. <Vehicle>['display_name']
  - define events and notifications
  - run server in background, interact with it through cmd interpreter and web interface
* Command Interpreter
  - choose (proper) subset of selected vehicles to operate on
  - print various (formatted) bits of the vehicle information
  - use jsonPath to extract different parts of the info across multiple vehicles
  - would like to be able to start with/without CI -- and even detach and reattach while it's running
* Web Interface
  - use maps to plot location, show trigger regions
  - graphically define/edit trigger regions
* Tracker
  - one per selected vehicle (for failure indepencence and concurrency -- maybe for dynamic start/stop too)
  - takes list of triggers and generates notification events of the desired type
  - register/unregister triggers -- or restart and give it triggers at start?
* Triggers
  - triggers are things that generate notifications
    * can be associated with multiple different notification mechanisms
    * can be stored persistently in config file, or added ephermerally via the cli
      - cli can also allow triggers to be persisted -- written into the config file
    * triggers represented by a TriggerSpec (cheap serialization approach)
      - a JSON object containing parameters needed to create a Trigger instance?
      - maybe make it a data object instead?
  - Trigger Events
    * location enters/exits a defined Trigger Region
    * value goes outside of a defined range of values
    * location changes by at least some delta
    * value changes by at least some delta
    * example events:
      - odometer increased by <delta> over last odometer event
      - odometer exceeds <value>
      - 'shift_state' change
      - 'shift_state' transition (<fromState>, <toState>) ???? not like the others ????
      - vehicle enters <region>
      - vehicle exits <region>
    * extend events to include:
      - climate outside range (<minTemp>, <maxTemp>)
      - climate changes by <deltaValue>
  - Trigger Regions:
    * circle: (lat, lon, radius) -- point is degenerate circle
    * polygon: [(lat,lon), ...] -- rectangle is special case polygon
* Notifications
  - different types: e.g.,
    * log
    * SMS
    * push notifications to mobile app
    * email
  - same interface (ABC/Protocol)
  - associated with triggers, can have multiple notifications associated with a given trigger instance
* Main Objects
  - CommandInterpreter
    * runs as MP process, has 'run()' method
    * is given inQ and outQ, and tesla object
    * sends TriggerSpec msgs to main loop to add Triggers to Trackers
    * can shut down via cli, and can restart via signal
    * gets msgs on inQ:
      - (cooked) inputs from stdin (from main loop)
      - shut down
    * sends msgs on outQ:
      - shut down Trackers and application
      - add trigger to Tracker(s)
  - Tracker
    * runs as MP process, has 'run()' method
    * is given inQ and outQ, and tesla object
    * one instance per selected vehicle
    * can get TriggerSpecs (from config file) at instantiation
    * gets msgs on inQ:
      - delete a current Trigger
      - create a new trigger based on a TriggerSpec
      - shut down
  - TriggerSpec
    * JSON string or Data Object?
    * parameters given to Trigger to instantiate (kwargs)
    * indicates type of trigger, which vehicle(s) it should be applied to, and type-specific args
    * can be stored in config file
  - Trigger
    * base class that has 'eval()' method
      - takes live/cached/updated vehicle state as input
      - returns bool indicating if the trigger has fired or not
    * trigger-type-specific subclasses
      - location-based
        * enter/exit Region
      - value-based (state-change (delta, specific state transition), enter/exit range)
        * odometer: vehicle_state
        * speed: drive_state
        * shift_state: drive_state
        * is_user_present: vehicle_state
        * locked: vehicle_state
        * battery_level: charge_state
        * inside_temp: climate_state
      - ETA?
        * estimated time to location given current state (location & speed)
  - Region
    * base class with constructors for specific type
      - method for evaluating whether a given position (lat,lon) is inside or outside the region
        * takes position (lat,lon) and returns bool (in/out)
      - also distance from position to nearest point in region
        * negative values means inside region?
    * subclasses for different types of regions -- circle, polygon
  - Notifier
    * common base class, subclasses for each supported notification mechanism
      - and notify() method
    * parameters needed to instantiate notification mechanisms can be included in config file
