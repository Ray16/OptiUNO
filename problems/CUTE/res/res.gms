* GAMS-model res.dag.gms written by dag2gams Converter at 29/03/2004 16:59:07
* University of Vienna
$offdigit;
 Set i/1*9/;
 Set j/1*18/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1.. -x('1') + 
x('3') + 
x('6') =e= 0;
con2.. -x('5') + 
x('6') - 
x('16') =e= 0;
con3.. x('7') - 
x('12') - 
x('15') =e= 0;
con4.. -x('1') + 
1.5 * x('12') =e= 0;
con5.. -x('2') + 
x('11') =e= -2;
con6.. x('12') - 
x('13') + 
x('14') =e= 0;
con7.. x('8') + 
x('12') - 
x('15') =e= 0;
con8..x('10') - 
x('18') =l= 0;
con9..x('9') - 
x('17') =l= 0;
x.lo('3')=0;
x.up('3')=0;
x.lo('4')=0;
x.up('4')=0;
x.lo('5')=0;
x.up('5')=0;
x.lo('9')=0;
x.up('9')=0;
x.lo('10')=0;
x.up('10')=0;
x.lo('1')=0;
x.up('1')=100;
x.lo('2')=0;
x.up('2')=100;
x.lo('6')=0;
x.up('6')=50;
x.lo('7')=0;
x.up('7')=30;
x.lo('8')=0;
x.up('8')=30;
x.lo('11')=0.5;
x.up('11')=50;
x.lo('12')=0.10000000000000001;
x.up('12')=10;
x.lo('13')=0;
x.up('13')=20;
x.lo('14')=0;
x.up('14')=10;
x.lo('15')=0.10000000000000001;
x.up('15')=30;
x.lo('16')=0;
x.up('16')=50;
x.lo('17')=100;
x.up('17')=1000;
x.lo('18')=100;
x.up('18')=1000;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


