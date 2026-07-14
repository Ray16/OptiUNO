* GAMS-model hs074.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*5/;
 Set j/1*4/;
 Equations objcon
con1
con2
con3
con4
con5
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 3 * x('3') + 
2 * x('4') + 
9.9999999999999995e-07 * power(x('3'), 3) + 
6.666666666666666e-07 * power(x('4'), 3);


con1..-x('1') + 
x('2') =g= -0.55000000000000004;
con2..-x('1') + 
x('2') =l= 0.55000000000000004;
con3.. 1000 * sin(x('2') - 0.25) + 
1000 * sin(-x('1') + 
x('2') - 
0.25) =e= -1294.8;
con4.. (-1000) * sin(x('1') - 0.25) - 
1000 * sin(x('1') - 
x('2') - 
0.25) + 
x('4') =e= 894.79999999999995;
con5.. (-1000) * sin((- x('1')) - 0.25) - 
1000 * sin((- x('2')) - 0.25) + 
x('3') =e= 894.79999999999995;
x.lo('1')=-0.55000000000000004;
x.up('1')=0.55000000000000004;
x.lo('2')=-0.55000000000000004;
x.up('2')=0.55000000000000004;
x.lo('3')=0;
x.up('3')=1200;
x.lo('4')=0;
x.up('4')=1200;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


