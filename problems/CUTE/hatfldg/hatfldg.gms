* GAMS-model hatfldg.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*25/;
 Set j/1*25/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
con11
con12
con13
con14
con15
con16
con17
con18
con19
con20
con21
con22
con23
con24
con25
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1.. x('2') - 
x('13') + 
x('2') * (x('1') - 
x('3')) =e= -1;
con2.. x('3') - 
x('13') + 
x('3') * (x('2') - 
x('4')) =e= -1;
con3.. -x('13') + 
x('25') + 
x('24') * x('25') =e= -1;
con4.. x('1') - 
x('13') - 
x('1') * x('2') =e= -1;
con5.. x('4') - 
x('13') + 
x('4') * (x('3') - 
x('5')) =e= -1;
con6.. -x('13') + 
x('24') + 
x('24') * (x('23') - 
x('25')) =e= -1;
con7.. x('5') - 
x('13') + 
x('5') * (x('4') - 
x('6')) =e= -1;
con8.. -x('13') + 
x('23') + 
x('23') * (x('22') - 
x('24')) =e= -1;
con9.. x('6') - 
x('13') + 
x('6') * (x('5') - 
x('7')) =e= -1;
con10.. -x('13') + 
x('22') + 
x('22') * (x('21') - 
x('23')) =e= -1;
con11.. x('7') - 
x('13') + 
x('7') * (x('6') - 
x('8')) =e= -1;
con12.. -x('13') + 
x('21') + 
x('21') * (x('20') - 
x('22')) =e= -1;
con13.. x('8') - 
x('13') + 
x('8') * (x('7') - 
x('9')) =e= -1;
con14.. -x('13') + 
x('20') + 
x('20') * (x('19') - 
x('21')) =e= -1;
con15.. x('9') - 
x('13') + 
x('9') * (x('8') - 
x('10')) =e= -1;
con16.. -x('13') + 
x('19') + 
x('19') * (x('18') - 
x('20')) =e= -1;
con17.. x('10') - 
x('13') + 
x('10') * (x('9') - 
x('11')) =e= -1;
con18.. -x('13') + 
x('18') + 
x('18') * (x('17') - 
x('19')) =e= -1;
con19.. x('11') - 
x('13') + 
x('11') * (x('10') - 
x('12')) =e= -1;
con20.. -x('13') + 
x('17') + 
x('17') * (x('16') - 
x('18')) =e= -1;
con21.. x('12') - 
x('13') + 
x('12') * (x('11') - 
x('13')) =e= -1;
con22.. -x('13') + 
x('16') + 
x('16') * (x('15') - 
x('17')) =e= -1;
con23.. x('13') * (x('12') - 
x('14')) =e= -1;
con24.. -x('13') + 
x('15') + 
x('15') * (x('14') - 
x('16')) =e= -1;
con25.. -x('13') + 
x('14') + 
x('14') * (x('13') - 
x('15')) =e= -1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


