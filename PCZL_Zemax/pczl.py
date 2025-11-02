import numpy as np
import math

class PCZL:
    '''
    PCZL (Positive Compensated Zoom Lens) is a class that simulates a zoom system which has a variator lens with a negative focal length and compensator lens with a positive focal length. The lenses are arranged in such a way that the system can zoom in and out while maintaining total track. All lenses are assumed to be thin lenses.  

    Attributes:
        f_2: float
            Normalized focal length of the variator. default is -1.0.
        f_3: float
            Normalized focal length of the compensator. default is 1.2.
        m_2l: float
            Axial magnification of the variator lens of long-focal-length position. default is -1.2.
        m_4: float
            Axial magnification of the rear fixed group at the shortest focal length position. default is 1.6.
        q: float
            The maximum movement of the variator lens from the longest focal length position to the shortest focal length position. default is 1.0.
        d_12s: float
            The distance between the front fixed group and the variator lens at the shortest focal length position. default is 0.5.
        d_34s: float
            The distance between the compensator lens and the rear fixed group at the shortest focal length position. default is 0.5.
        num_samples: int
            The number of samples for the variator lens movement. default is 100.
    '''

    f_2: float = -1.0
    f_3: float = 1.2
    m_2l: float = -1.0
    m_4: float = 1.6
    q: float = 1.0
    d_12s: float = 0.2
    d_34s: float = 0.15
    num_samples: int = 100

    def __init__(self, f_2=-1.0, f_3=1.2, m_2l=-1.0, m_4 = 1.6, q=1.0, d_12s=0.2, d_34s=0.15, num_samples=100):
        '''
        Initializes the PCZL with the given parameters.
        '''
        self.f_2 = f_2
        self.f_3 = f_3
        self.m_2l = m_2l
        self.m_4 = m_4
        self.q = q
        self.d_12s = d_12s
        self.d_34s = d_34s
        self.num_samples = num_samples
    
    @property
    def q_2(self):
        '''
        The range of the variator lens movement from the longest focal length position  to the longest focal length position. 
        '''
        q_2 = np.linspace(0, self.q, self.num_samples)
        return q_2
    
    @property
    def d_23l(self):
        '''
        Calculates the distance between the variator and compensator lenses at the longest focal length position.
        '''
        d_23l = 2.0 * self.f_3 - 2.0
        return d_23l

    @property
    def m_2(self):
        '''
        Calculates the axial magnification range of the variator lens 
        '''
        m_2 = 1.0 / (1.0 / self.m_2l + self.q_2 / self.f_2)
        return m_2

    @property
    def m_3l(self):
        '''
        Calculates the axial magnification of the compensator lens at the longest focal length position.
        '''
        m_3l = self.f_3 / (self.f_2 * (1.0 - self.m_2l) - self.d_23l + self.f_3)
        return m_3l

    @property
    def b(self):
        '''
        Calculates the b parameter which is used to calculate the axial magnification of the compensator lens.
        '''
        b = (self.f_2 / self.f_3) * (1.0 / self.m_2l - 1.0 / self.m_2 + self.m_2l - self.m_2) + 1.0 / self.m_3l + self.m_3l
        return b

    @property
    def m_3(self):
        '''
        Calculates the axial magnification range of the compensator lens.
        '''
        m_3 = (self.b + np.sqrt(self.b**2 - 4.0)) / 2.0
        return m_3

    @property
    def Delta(self):
        '''
        Calculates the movement of the compensator lens from the longest focal length position.
        '''
        Delta = self.f_3 * (self.m_3 - self.m_3l)
        return Delta

    @property
    def d_12(self):
        '''
        Calculates the distance between the front fixed group and the variator lens from the longest focal length position to the shortest focal length position.
        '''
        d_12 = self.d_12s + self.q_2
        return d_12[::-1]
    
    @property
    def d_23(self):
        ''' 
        Calculates the distance between the variator and compensator lenses from the longest focal length position to the shortest focal length position.
        '''
        d_23 = self.d_23l + self.Delta + self.q_2
        return d_23
    
    @property
    def d_34(self):
        '''
        Calculates to the shortest focal length position.
        '''
        d_34 = self.d_34s + self.Delta
        return d_34[::-1]
    
    @property
    def f_1(self):
        '''
        Calculates the focal length of the front fixed group, assuming the abject is at infinite position.
        '''
        f_1 = self.d_12[-1] + self.f_2 * (1.0 - self.m_2[-1]) / self.m_2[-1]
        return f_1
    
    @property
    def l_4o(self):
        '''
        Calculates the object distance of the rear fixed group from the longest focal position to the shortest focal length position.
        '''
        l_1o = math.inf
        l_1i = 1.0 / (1.0 / self.f_1 - 1.0 / l_1o)
        l_2o = self.d_12 - l_1i
        l_2i = 1.0 / (1.0 / self.f_2 - 1.0 / l_2o)
        l_3o = self.d_23 - l_2i
        l_3i = 1.0 / (1.0 / self.f_3 - 1.0 / l_3o)
        l_4o = self.d_34 - l_3i
        return l_4o[0]

    @property
    def f_4(self):
        '''
        Calculates the focal length of the rear fixed group.
        '''
        f_4 = self.l_4o / (1.0 - 1.0 / self.m_4)
        return f_4
    
    @property
    def l_4i(self):
        '''
        Calculates the image distance of the rear fixed group from the longest focal position to the shortest focal length position.
        '''
        l_4i = - self.m_4 * self.l_4o
        return l_4i
    
    @property
    def total_track(self):
        '''
        Calculates the total track of the PCZL system from the front group to the image plane at every position, ranging from the longest focal position.
        '''
        total_track = self.d_12 + self.d_23 + self.d_34 + self.l_4i
        return total_track

    @property
    def zoom_ratio(self):
        '''
        Calculates the zoom ratios of the PCZL system.
        '''
        gamma = self.m_2l * self.m_3l / (self.m_2 * self.m_3)
        return gamma
    
    @property
    def f_max(self):
        '''
        Calculates the maximum longest focal length of the PCZL system.
        '''
        f_max = self.f_1 * self.m_2l * self.m_3l * self.m_4
        return f_max
    
    @property
    def f_min(self):
        '''
        Calculates the minimum shortest focal length of the PCZL system.
        '''
        f_min = self.f_1 * self.m_2[-1] * self.m_3[-1] * self.m_4
        return f_min