import numpy as np

# Annahme: arr ist das ursprüngliche Array mit der Form (555, 4, 45)
arr = np.random.rand(555, 4, 45)

# Neues Array mit der gewünschten Form erstellen
new_shape = (arr.shape[0], 3, 4, 15)
arr_reshaped = arr.reshape(new_shape)

# Überprüfung der Werte vor und nach der Umformung
are_equal = np.array_equal(arr.flatten(), arr_reshaped.flatten())

if are_equal:
    print("Die Umformung war erfolgreich.")
else:
    print("Die Umformung war nicht erfolgreich.")
