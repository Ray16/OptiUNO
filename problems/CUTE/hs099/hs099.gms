* GAMS-model hs099.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*14/;
 Set j/1*23/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(power(1250 * cos(x('1')) + 
1250 * cos(x('2')) + 
3750 * cos(x('3')) + 
3750 * cos(x('4')) + 
3750 * cos(x('5')) + 
9000 * cos(x('6')) + 
9000 * cos(x('7')), 2));


con1.. (-9000) * sin(x('7')) - 
x('22') + 
x('23') =e= -2880;
con2.. (-9000) * sin(x('6')) - 
x('21') + 
x('22') =e= -2880;
con3.. (-3750) * sin(x('5')) - 
x('20') + 
x('21') =e= -1600;
con4.. (-3750) * sin(x('4')) - 
x('19') + 
x('20') =e= -1600;
con5.. (-3750) * sin(x('3')) - 
x('18') + 
x('19') =e= -1600;
con6.. (-1250) * sin(x('2')) - 
x('17') + 
x('18') =e= -800;
con7.. (-1250) * sin(x('1')) - 
x('16') + 
x('17') =e= -800;
con8.. (-405000) * sin(x('7')) - 
x('14') + 
x('15') - 
90 * x('22') =e= -129600;
con9.. (-405000) * sin(x('6')) - 
x('13') + 
x('14') - 
90 * x('21') =e= -129600;
con10.. (-93750) * sin(x('5')) - 
x('12') + 
x('13') - 
50 * x('20') =e= -40000;
con11.. (-15625) * sin(x('1')) - 
x('8') + 
x('9') - 
25 * x('16') =e= -10000;
con12.. (-93750) * sin(x('4')) - 
x('11') + 
x('12') - 
50 * x('19') =e= -40000;
con13.. (-15625) * sin(x('2')) - 
x('9') + 
x('10') - 
25 * x('17') =e= -10000;
con14.. (-93750) * sin(x('3')) - 
x('10') + 
x('11') - 
50 * x('18') =e= -40000;
x.lo('23')=1000;
x.up('23')=1000;
x.lo('15')=100000;
x.up('15')=100000;
x.lo('8')=-0;
x.up('8')=0;
x.lo('16')=-0;
x.up('16')=0;
x.lo('1')=0;
x.up('1')=1.5800000000000001;
x.lo('2')=0;
x.up('2')=1.5800000000000001;
x.lo('3')=0;
x.up('3')=1.5800000000000001;
x.lo('4')=0;
x.up('4')=1.5800000000000001;
x.lo('5')=0;
x.up('5')=1.5800000000000001;
x.lo('6')=0;
x.up('6')=1.5800000000000001;
x.lo('7')=0;
x.up('7')=1.5800000000000001;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


