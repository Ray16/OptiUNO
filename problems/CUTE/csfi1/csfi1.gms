* GAMS-model csfi1.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*5/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
con4
con5
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(x('3'));


con1.. 117.370892 * ((x('3')) / (x('1') * x('2'))) - 
x('4') =e= 0;
con2.. -x('5') + 
0.020833333333333332 * x('4') * power(x('1'), 2) =e= 0;
con3..x('2') / x('1') =l= 2;
con4..x('1') * x('2') =g= 200;
con5..x('1') * x('2') =l= 250;
x.lo('1')=7;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
x.up('5')=60;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


