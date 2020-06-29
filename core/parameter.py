import logging

class Parameter(object):
    """
    Generic handler for parameters stored in configuration files

    Attributes:
        parameters          dictionary containing the value for configuration parameters
        default_parameters  dictionary containung default values for parameters
    """
    def __init__(self, parameter_filename):
        self.parameters = {}
        self.default_parameters = {}
        if parameter_filename is None:
            logging.warning("No parameter file provided; using default parameters")
        else:
            logging.info("Extract parameters from file {}".format(parameter_filename))
            self.load_parameter_file(parameter_filename)

    def load_parameter_file(self, parameter_filename):
        with open(parameter_filename) as f:
            for line in f.readlines():
                # Ignore comments
                if line.startswith("#"):
                    continue

                try:
                    # Also get rid of trailing characters
                    key, value = line.strip().split(":")
                    if key in self.parameters:
                        if not isinstance(self.parameters[key], list):
                            self.parameters[key] = [self.parameters[key]]
                        self.parameters[key].append(value)
                    else:
                        self.parameters[key] =  value
                except ValueError as e:
                    logging.warning(
                        "Got error '{}' for line '{}'; ignore it".format(e, line))

    def get(self, key):
        """
        Get the value of the parameter with key `key`.
        If not defined by the configuration file, return the default value.
        Raise Exception if the parameter has no default value and is absent.
        """
        val = self.parameters.get(key)
        if val is None:
            if key in self.default_parameters:
                return self.default_parameters[key]
            else:
                raise Exception("Parameter not found " + key)
        else:
            return val

    def __str__(self):
        return self.parameters.__str__()
