swagger_template = {
    "openapi": "3.0.0",
    "info": {
        "title": "Fleet API",
        "version": "1.0.0",
        "description": "API to manage employees, carriages, trains, and maintenances."
    },
    "paths": {
        # Employees
        "/employees": {
            "get": {
                "tags": ["Employees"],
                "summary": "Retrieve all Employees",
                "description": "Returns all employees.",
                "responses": {
                    "200": {
                        "description": "List of all employees.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Employee"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Employees"],
                "summary": "Create new Employee",
                "description": "Creates an employee with the provided data.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/EmployeeCreate"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Employee successfully created.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Employee"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data provided."
                    }
                }
            }
        },
        "/employees/{ssn}": {
            "put": {
                "tags": ["Employees"],
                "summary": "Update an Employee",
                "description": "Updates an existing employee by SSN.",
                "parameters": [
                    {
                        "name": "ssn",
                        "in": "path",
                        "description": "SSN of the employee to update",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/EmployeeUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Employee successfully updated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Employee"}
                            }
                        }
                    },
                    "400": {
                        "description": "Validation error."
                    },
                    "404": {
                        "description": "Employee not found."
                    }
                }
            },
            "delete": {
                "tags": ["Employees"],
                "summary": "Delete an Employee",
                "description": "Deletes an employee by SSN.",
                "parameters": [
                    {
                        "name": "ssn",
                        "in": "path",
                        "description": "SSN of the employee to delete",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Employee successfully deleted.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Cannot delete employee with existing maintenances."
                    },
                    "404": {
                        "description": "Employee not found."
                    }
                }
            }
        },

        # Carriages
        "/fleet/carriages": {
            "get": {
                "tags": ["Carriages"],
                "summary": "Retrieve all Carriages",
                "description": "Returns all railcars and passenger cars.",
                "responses": {
                    "200": {
                        "description": "List of all carriages.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Carriage"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Carriages"],
                "summary": "Create new Carriage",
                "description": "Creates either a Railcar or a PassengerCar.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CarriageCreate"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Carriage successfully created.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Carriage"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data."
                    }
                }
            }
        },
        "/fleet/carriages/{carriage_id}": {
            "put": {
                "tags": ["Carriages"],
                "summary": "Update a Carriage",
                "description": "Updates an existing carriage by carriage ID.",
                "parameters": [
                    {
                        "name": "carriage_id",
                        "in": "path",
                        "description": "ID of the carriage to update",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CarriageUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Carriage successfully updated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Carriage"}
                            }
                        }
                    },
                    "400": {
                        "description": "Cannot edit carriage assigned to a train or invalid data."
                    },
                    "404": {
                        "description": "Carriage not found."
                    }
                }
            },
            "delete": {
                "tags": ["Carriages"],
                "summary": "Delete a Carriage",
                "description": "Deletes a carriage by carriage ID.",
                "parameters": [
                    {
                        "name": "carriage_id",
                        "in": "path",
                        "description": "ID of the carriage to delete",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Carriage successfully deleted.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Cannot delete carriage assigned to a train."
                    },
                    "404": {
                        "description": "Carriage not found."
                    }
                }
            }
        },

        # Trains
        "/fleet/trains": {
            "get": {
                "tags": ["Trains"],
                "summary": "Retrieve all Trains",
                "description": "Returns the list of trains including assigned railcars and passenger cars.",
                "responses": {
                    "200": {
                        "description": "List of trains.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Train"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Trains"],
                "summary": "Create new Train",
                "description": "Assigns a railcar and passenger cars to form a train. Checks track gauge and tractive force constraints.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TrainCreate"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Train successfully created.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Train"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data or constraints not met."
                    },
                    "404": {
                        "description": "Railcar or PassengerCar not found."
                    }
                }
            }
        },
        "/fleet/trains/{train_id}": {
            "put": {
                "tags": ["Trains"],
                "summary": "Update a Train",
                "description": "Updates an existing train by train ID.",
                "parameters": [
                    {
                        "name": "train_id",
                        "in": "path",
                        "description": "ID of the train to update",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TrainUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Train successfully updated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Train"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data or constraints not met."
                    },
                    "404": {
                        "description": "Train not found."
                    }
                }
            },
            "delete": {
                "tags": ["Trains"],
                "summary": "Delete a Train",
                "description": "Deletes a train by train ID.",
                "parameters": [
                    {
                        "name": "train_id",
                        "in": "path",
                        "description": "ID of the train to delete",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Train successfully deleted.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Cannot delete train with existing maintenance."
                    },
                    "404": {
                        "description": "Train not found."
                    }
                }
            }
        },

        # Maintenances
        "/fleet/maintenance": {
            "get": {
                "tags": ["Maintenances"],
                "summary": "Retrieve all Maintenances",
                "description": "Returns all maintenance entries with times and employees.",
                "responses": {
                    "200": {
                        "description": "List of maintenances.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Maintenance"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "tags": ["Maintenances"],
                "summary": "Create new Maintenance",
                "description": "Assigns an employee to maintain a train from_time to to_time. Checks for schedule overlaps.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MaintenanceCreate"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Maintenance successfully created.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Maintenance"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data or overlap error."
                    },
                    "404": {
                        "description": "Employee or Train not found."
                    }
                }
            }
        },
        "/fleet/maintenance/{maintenance_id}": {
            "put": {
                "tags": ["Maintenances"],
                "summary": "Update a Maintenance",
                "description": "Updates an existing maintenance record by maintenance ID.",
                "parameters": [
                    {
                        "name": "maintenance_id",
                        "in": "path",
                        "description": "ID of the maintenance to update",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MaintenanceUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Maintenance successfully updated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Maintenance"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid data or overlap error."
                    },
                    "404": {
                        "description": "Maintenance not found."
                    }
                }
            },
            "delete": {
                "tags": ["Maintenances"],
                "summary": "Delete a Maintenance",
                "description": "Deletes a maintenance record by maintenance ID.",
                "parameters": [
                    {
                        "name": "maintenance_id",
                        "in": "path",
                        "description": "ID of the maintenance to delete",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Maintenance successfully deleted.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Maintenance not found."
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            # Employee
            "Employee": {
                "type": "object",
                "properties": {
                    "ssn": {"type": "string"},
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "password": {"type": "string"},
                    "department": {"type": "string", "enum": ["Crew", "Maintenance"]},
                    "role": {"type": "string", "enum": ["Admin", "Employee"]},
                    "username": {"type": "string"}
                }
            },
            "EmployeeCreate": {
                "type": "object",
                "properties": {
                    "ssn": {"type": "string"},
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "password": {"type": "string"},
                    "department": {"type": "string", "enum": ["Crew", "Maintenance"]},
                    "role": {"type": "string", "enum": ["Admin", "Employee"]},
                    "username": {"type": "string"}
                },
                "required": ["ssn", "firstName", "lastName", "password", "department", "role"]
            },
            "EmployeeUpdate": {
                "type": "object",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "password": {"type": "string"},
                    "department": {"type": "string", "enum": ["Crew", "Maintenance"]},
                    "role": {"type": "string", "enum": ["Admin", "Employee"]},
                    "username": {"type": "string"}
                }
            },

            # Carriage
            "Carriage": {
                "type": "object",
                "properties": {
                    "carriageID": {"type": "integer"},
                    "trackGauge": {"type": "string"},
                    "type": {"type": "string"},
                    "maxTractiveForce": {"type": "integer"},
                    "numberOfSeats": {"type": "integer"},
                    "maxWeight": {"type": "integer"}
                }
            },
            "CarriageCreate": {
                "type": "object",
                "properties": {
                    "trackGauge": {"type": "string"},
                    "type": {"type": "string", "enum": ["Railcar", "PassengerCar"]},
                    "maxTractiveForce": {"type": "integer"},
                    "numberOfSeats": {"type": "integer"},
                    "maxWeight": {"type": "integer"}
                },
                "required": ["trackGauge", "type"]
            },
            "CarriageUpdate": {
                "type": "object",
                "properties": {
                    "trackGauge": {"type": "string"},
                    "type": {"type": "string", "enum": ["Railcar", "PassengerCar"]},
                    "maxTractiveForce": {"type": "integer"},
                    "numberOfSeats": {"type": "integer"},
                    "maxWeight": {"type": "integer"}
                }
            },

            # Train
            "Train": {
                "type": "object",
                "properties": {
                    "trainID": {"type": "integer"},
                    "name": {"type": "string"},
                    "railcarID": {"type": "integer"},
                    "passengerCars": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "position": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            "TrainCreate": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "railcarID": {"type": "integer"},
                    "passengerCars": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "position": {"type": "integer"}
                            },
                            "required": ["id", "position"]
                        }
                    }
                },
                "required": ["name", "railcarID", "passengerCars"]
            },
            "TrainUpdate": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "railcarID": {"type": "integer"},
                    "passengerCars": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "position": {"type": "integer"}
                            },
                            "required": ["id", "position"]
                        }
                    }
                }
            },

            # Maintenance
            "Maintenance": {
                "type": "object",
                "properties": {
                    "maintenanceID": {"type": "integer"},
                    "employeeSSN": {"type": "string"},
                    "trainID": {"type": "integer"},
                    "from_time": {"type": "string", "format": "date-time"},
                    "to_time": {"type": "string", "format": "date-time"}
                }
            },
            "MaintenanceCreate": {
                "type": "object",
                "properties": {
                    "employeeSSN": {"type": "string"},
                    "trainID": {"type": "integer"},
                    "from_time": {"type": "string", "format": "date-time"},
                    "to_time": {"type": "string", "format": "date-time"}
                },
                "required": ["employeeSSN", "trainID", "from_time", "to_time"]
            },
            "MaintenanceUpdate": {
                "type": "object",
                "properties": {
                    "employeeSSN": {"type": "string"},
                    "trainID": {"type": "integer"},
                    "from_time": {"type": "string", "format": "date-time"},
                    "to_time": {"type": "string", "format": "date-time"}
                }
            }
        }
    }
}