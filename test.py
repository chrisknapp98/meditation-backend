# Class to test some stuff during development
import numpy as np

existing_array = np.array([70,65,60,55,50,55,60,65,70, 75, 80, 85, 90])
additional_values = 15

# Lineare Interpolation
interp_indices = np.linspace(0, len(existing_array) - 1, additional_values)
interpolated_values = np.interp(interp_indices, np.arange(len(existing_array)), existing_array)
complete_array = np.concatenate([existing_array, interpolated_values.round().astype(int)])
print(complete_array)