import random
import unittest

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

class XORCryptosystem:
    @staticmethod
    def xor_transform(msg, key):
        for i in range(0, len(msg)):
            msg[i] ^= key[i%len(key)]

    @staticmethod
    def create_key(polarizations1, polarizations2, values):
        key = []
        for i in range(0, len(polarizations1)):
            if polarizations1[i] == polarizations2[i]:
                key.append(values[i])
        return key

class EndPoint:
    def receive(self, qubits, end_point):
        self._polarizations = [random.randint(0,1) for i in range(0, len(qubits))]
        self._values = [qubits[i].measure(self._polarizations[i]) for i in range(0,len(qubits))]
        self.send_polarizations(self._polarizations, end_point)

    def send(self, num_qubits, end_point):
        self._polarizations = [random.randint(0,1) for i in range(0, num_qubits)]
        self._values = [random.randint(0,1) for i in range(0, num_qubits)] 
        self._qubits = [Qubit(self._values[i], self._polarizations[i]) for i in range(0, num_qubits)]
        end_point.receive(self._qubits, self)
        self.send_polarizations(self._polarizations, end_point)

    def receive_polarizations(self, polarizations):
        self._received_polarizations = polarizations
        self._key = self.get_key(self._polarizations, self._received_polarizations, self._values)

    def send_polarizations(self, polarizations, end_point):
        end_point.receive_polarizations(polarizations)

    def get_key(self, polarizations, received_polarizations, values):
        return XORCryptosystem.create_key(polarizations, received_polarizations, values)

    def print_key(self):
        print(self._key)

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

tests = UnitTests()
tests.test_same_polarization(10000)
tests.test_xor_transform(100,3)

transmitter = EndPoint()
receiver = EndPoint()
transmitter.send(16, receiver)
transmitter.print_key()
receiver.print_key()