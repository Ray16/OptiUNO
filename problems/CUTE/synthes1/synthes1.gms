* GAMS-model synthes1.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*6/;
 Set j/1*6/;
 Equations objcon
con1
con2
con3
con4
con5
con6
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-18) * log(x('2') + 1) - 
19.199999999999999 * log(x('1') - 
x('2') + 
1) + 
10 * x('1') - 
7 * x('3') + 
5 * x('4') + 
6 * x('5') + 
8 * x('6') + 10;


con1..-x('4') - 
x('5') =g= -1;
con2..-x('1') + 
x('2') + 
2 * x('5') =g= 0;
con3..-x('2') + 
2 * x('4') =g= 0;
con4..x('1') - 
x('2') =g= 0;
con5..-log(x('2') + 1) - 
1.2 * log(x('1') - 
x('2') + 
1) + 
x('3') + 
2 * x('6') =l= 2;
con6..(-0.80000000000000004) * log(x('2') + 1) - 
0.95999999999999996 * log(x('1') - 
x('2') + 
1) + 
0.80000000000000004 * x('3') =l= 0;
x.lo('1')=0;
x.up('1')=2;
x.lo('2')=0;
x.up('2')=2;
x.lo('3')=0;
x.up('3')=1;
x.lo('4')=0;
x.up('4')=1;
x.lo('5')=0;
x.up('5')=1;
x.lo('6')=0;
x.up('6')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


