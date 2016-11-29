# -*- coding: utf-8 -*-
"""
Tests of the Coax class
"""
import unittest
from tresonator import Coax

class TestCoax(unittest.TestCase):
    
    def test_Coax_constructor_bad_value_L(self):       
        with self.assertRaises(ValueError):
            Coax(L=0, Dint=1, Dout=1)
        
    def test_Coax_constructor_bad_value_Dint(self):       
        with self.assertRaises(ValueError):
            Coax(L=1, Dint=0, Dout=1)
        
    def test_Coax_constructor_bad_value_Dout(self):       
        with self.assertRaises(ValueError):
            Coax(L=1, Dint=1, Dout=0)
            
    def test_Coax_positive_Zc(self):
        co = Coax(L=1, Dint=1, Dout=2)
        self.assertGreater(co.Zc, 0)
        
    def test_Coax_constructor_bad_value_Din_Dout(self):       
        with self.assertRaises(ValueError):
            Coax(L=1, Dint=2, Dout=2) # Dint=Dout
            
    def test_Coax_alpha_negative_frequency(self):       
        with self.assertRaises(ValueError):
            co = Coax(L=1, Dint=2, Dout=3) 
            co.alpha(f=0)
            
    def test_Coax_gamma_negative_frequency(self):       
        with self.assertRaises(ValueError):
            co = Coax(L=1, Dint=2, Dout=3) 
            co.gamma(f=0)        

