from dataclasses import dataclass


@dataclass
class GstState:
    name: str
    title: str
    code: int


indian_states: list[GstState] = [
    GstState(code=1, name='JK', title='Jammu and Kashmir'),
    GstState(code=2, name='HP', title='Himachal Pradesh'),
    GstState(code=3, name='PB', title='Punjab'),
    GstState(code=4, name='CH', title='Chandigarh'),
    GstState(code=5, name='UT', title='Uttarakhand'),
    GstState(code=6, name='HR', title='Haryana'),
    GstState(code=7, name='DL', title='Delhi'),
    GstState(code=8, name='RJ', title='Rajasthan'),
    GstState(code=9, name='UP', title='Uttar Pradesh'),
    GstState(code=10, name='BR', title='Bihar'),
    GstState(code=11, name='SK', title='Sikkim'),
    GstState(code=12, name='AR', title='Arunachal Pradesh'),
    GstState(code=13, name='NL', title='Nagaland'),
    GstState(code=14, name='MN', title='Manipur'),
    GstState(code=15, name='MZ', title='Mizoram'),
    GstState(code=16, name='TR', title='Tripura'),
    GstState(code=17, name='ML', title='Meghalaya'),
    GstState(code=18, name='AS', title='Assam'),
    GstState(code=19, name='WB', title='West Bengal'),
    GstState(code=20, name='JH', title='Jharkhand'),
    GstState(code=21, name='OR', title='Odisha'),
    GstState(code=22, name='CG', title='Chattisgarh'),
    GstState(code=23, name='MP', title='Madhya Pradesh'),
    GstState(code=24, name='GJ', title='Gujarat'),
    GstState(code=25, name='DD', title='Daman and Diu (old)'),
    GstState(code=26, name='DN', title='Dadra, Nagar Haveli, Daman and Diu'),
    GstState(code=27, name='MH', title='Maharashtra'),
    GstState(code=28, name='AP', title='Andhra Pradesh (old)'),
    GstState(code=29, name='KA', title='Karnataka'),
    GstState(code=30, name='GA', title='Goa'),
    GstState(code=31, name='LD', title='Lakshadweep'),
    GstState(code=32, name='KL', title='Kerala'),
    GstState(code=33, name='TN', title='Tamil Nadu'),
    GstState(code=34, name='PY', title='Puducherry'),
    GstState(code=35, name='AN', title='Andaman and Nicobar Islands'),
    GstState(code=36, name='TG', title='Telangana'),
    GstState(code=37, name='AD', title='Andhra Pradesh'),
    GstState(code=38, name='LA', title='Ladakh'),
]
indian_states.sort(key=lambda s: (s.title, s.code) if s.code < 90 else ('ZZ', s.code))


indian_states_dict = {state.name: state for state in indian_states}

codes = [state.code for state in indian_states]
