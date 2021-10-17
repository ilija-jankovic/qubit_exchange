import random
import unittest

#Quantum replacement for bits.
class Qubit:
    def __init__(self, value, polarization):
        self.set(value, polarization)
    
    def set(self, value, polarization):
        self._value = value
        self._polarization = polarization
    
    def measure(self, polarization):
        if self._polarization == polarization:
            return self._value
        self._polarization = polarization
        self._value = random.randint(0,1)
        return self._value

    def get_value(self):
        return self._value

    def get_polarization(self):
        return self._polarization

#Static methods for QKE and XOR cryptography.
class XORCryptosystem:
    #XOR bits of message and key. If the message is longer than the key, loop around with modulo.
    @staticmethod
    def xor_transform(msg, key):
        for i in range(0, len(msg)):
            msg[i] ^= key[i%len(key)]

    #Append values to key for which polarizations match
    @staticmethod
    def create_key(polarizations1, polarizations2, values):
        key = []
        for i in range(0, len(polarizations1)):
            if polarizations1[i] == polarizations2[i]:
                key.append(values[i])
        return key

#The transmitters and receivers of QKE.
class EndPoint:
    def receive(self, qubits, end_point):
        self._received_qubits = qubits
        self._polarizations = [random.randint(0,1) for i in range(0, len(qubits))]
        self._values = [qubits[i].measure(self._polarizations[i]) for i in range(0,len(qubits))]
        self.send_polarizations(self._polarizations, end_point)

    #Starts a chain reaction of sending qubits and sending/receiving polarizations to form symmetric keys.
    def send(self, num_qubits, end_point):
        self._polarizations = [random.randint(0,1) for i in range(0, num_qubits)]
        self._values = [random.randint(0,1) for i in range(0, num_qubits)] 
        self._qubits = [Qubit(self._values[i], self._polarizations[i]) for i in range(0, num_qubits)]
        end_point.receive(self._qubits, self)
        self.send_polarizations(self._polarizations, end_point)

    def receive_polarizations(self, polarizations):
        self._received_polarizations = polarizations
        self._key = XORCryptosystem.create_key(self._polarizations, self._received_polarizations, self._values)

    def send_polarizations(self, polarizations, end_point):
        end_point.receive_polarizations(polarizations)

    #Getter functions used for unit tests and man-in-the-middle scenario.

    def get_key(self):
        return self._key

    def get_received_polarizations(self):
        return self._received_polarizations

    def get_received_qubits(self):
        return self._received_qubits

#Unit tests for qubits, XOR cryptosystem, and QKE with end hosts.
class UnitTests(unittest.TestCase):
    def test_same_polarization(self, num_qubits):
        print("Measuring {0} qubits with same polarization for unchanged value...".format(num_qubits))
        for i in range(0, num_qubits):
            qubit = Qubit(random.randint(0,1), random.randint(0,1))
            expected_value = qubit.get_value()
            self.assertTrue(qubit.measure(qubit.get_polarization()) == expected_value, \
                "Expected value of {0} returned {1}".format(expected_value, qubit.get_value()))
        print("PASS")

    def test_xor_transform(self, msg_length, key_length):
        msg = [random.randint(0,1) for i in range(0, msg_length)]
        key = [random.randint(0,1) for i in range(0, key_length)]
        print("Tranforming message of length {0} with key of length {1} twice and comparing equality...".format(msg_length, key_length))
        expected_msg = msg.copy()
        XORCryptosystem.xor_transform(msg, key)
        XORCryptosystem.xor_transform(msg, key)
        self.assertTrue(len(msg) == len(expected_msg), "Transformed message not equal")
        for i in range(0, len(msg)):
            if msg[i] != expected_msg[i]:
               self.assertTrue(len(msg) == len(expected_msg), "Transformed message not equal") 
        print("PASS")

    def test_qke(self, num_qubits):
        print("Performing QKE with {0} qubits and comparing key equality...".format(num_qubits))
        transmitter = EndPoint()
        receiver = EndPoint()
        transmitter.send(num_qubits, receiver)
        key_t, key_r = transmitter.get_key(), receiver.get_key()
        self.assertTrue(len(key_t) == len(key_r), "Keys are not equal")
        for i in range(0, len(key_t)):
            self.assertTrue(key_t[i] == key_r[i], "Keys are not equal")
        print("PASS")

#A number of unit tests with different parameters.
tests = UnitTests()
tests.test_same_polarization(10000)
tests.test_xor_transform(100,3)
tests.test_xor_transform(40,62)
tests.test_qke(16)
tests.test_qke(256)
tests.test_qke(1024)

#Uses sent qubit and polarization data to crack a key and implied message.
class ManInTheMiddle:
    def __init__(self, polarizations_t, polarizations_r, qubits):
        self._polarizations_t = polarizations_t
        self._polarizations_r = polarizations_r
        self._qubits = qubits

    #If polarizations are the same, the value of the qubit must be the same as in the key if measured
    #against the transmitter's polarization.
    def crack_key(self):
        key = []
        for i in range(0, len(self._polarizations_t)):
            if self._polarizations_t[i] == self._polarizations_r[i]:
                key.append(self._qubits[i].measure(self._polarizations_t[i]))
        return key

#Man-in-the-middle attack scenario.
transmitter = EndPoint()
receiver = EndPoint()
transmitter.send(16, receiver)
middle = ManInTheMiddle(transmitter.get_received_polarizations(), \
    receiver.get_received_polarizations(), receiver.get_received_qubits())

msg = [i%2 for i in range(0,50)]
ciphertext = msg.copy()
XORCryptosystem.xor_transform(ciphertext, receiver.get_key())

cracked_key = middle.crack_key()
cracked_msg = ciphertext.copy()
XORCryptosystem.xor_transform(cracked_msg, cracked_key)

def int_list_to_str(list):
    return ''.join(map(str,list))

print("Man in the middle scenario:")
print("Message =", int_list_to_str(msg))
print("QKE key =", int_list_to_str(receiver.get_key()))
print("Ciphertext =", int_list_to_str(ciphertext))
print("Cracked key =", int_list_to_str(cracked_key))
print("Cracked message =", int_list_to_str(cracked_msg))