* GAMS-model hs99exp.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*21/;
 Set j/1*31/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(power(x('8'), 2));


con1.. 1250 * cos(x('1')) + 
x('9') - 
x('12') =e= 0;
con2.. 9000 * sin(x('7')) + 
x('29') - 
x('31') =e= 1000;
con3.. 15625 * sin(x('1')) + 
x('10') + 
25 * x('11') - 
x('13') =e= 10000;
con4.. 405000 * sin(x('7')) + 
x('28') + 
90 * x('29') - 
x('30') =e= 100000;
con5.. 9000 * cos(x('7')) - 
x('8') + 
x('27') =e= 0;
con6.. 9000 * sin(x('6')) + 
x('26') - 
x('29') =e= 2880;
con7.. 1250 * sin(x('1')) + 
x('11') - 
x('14') =e= 800;
con8.. 405000 * sin(x('6')) + 
x('25') + 
90 * x('26') - 
x('28') =e= 129600;
con9.. 1250 * cos(x('2')) + 
x('12') - 
x('15') =e= 0;
con10.. 9000 * cos(x('6')) + 
x('24') - 
x('27') =e= 0;
con11.. 3750 * sin(x('5')) + 
x('23') - 
x('26') =e= 1600;
con12.. 15625 * sin(x('2')) + 
x('13') + 
25 * x('14') - 
x('16') =e= 10000;
con13.. 93750 * sin(x('5')) + 
x('22') + 
50 * x('23') - 
x('25') =e= 40000;
con14.. 3750 * cos(x('5')) + 
x('21') - 
x('24') =e= 0;
con15.. 1250 * sin(x('2')) + 
x('14') - 
x('17') =e= 800;
con16.. 3750 * sin(x('4')) + 
x('20') - 
x('23') =e= 1600;
con17.. 93750 * sin(x('4')) + 
x('19') + 
50 * x('20') - 
x('22') =e= 40000;
con18.. 3750 * cos(x('3')) + 
x('15') - 
x('18') =e= 0;
con19.. 3750 * cos(x('4')) + 
x('18') - 
x('21') =e= 0;
con20.. 93750 * sin(x('3')) + 
x('16') + 
50 * x('17') - 
x('19') =e= 40000;
con21.. 3750 * sin(x('3')) + 
x('17') - 
x('20') =e= 1600;
x.lo('9')=0;
x.up('9')=0;
x.lo('10')=0;
x.up('10')=0;
x.lo('11')=0;
x.up('11')=0;
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
  


