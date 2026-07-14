* GAMS-model zangwil2.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-3.7333333333333334) * x('1') - 
17.066666666666666 * x('2') + 
1.0666666666666667 * power(x('1'), 2) + 
1.0666666666666667 * power(x('2'), 2) - 
0.53333333333333333 * x('1') * x('2') + 66.066666666666663;


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


