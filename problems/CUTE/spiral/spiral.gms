* GAMS-model spiral.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*3/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('3');


con1..((- (cos(sqrt(power(x('2'), 2) + 
power(x('1'), 2))) * sqrt(power(x('2'), 2) + 
power(x('1'), 2)))) + 
x('1')) * ((- (cos(sqrt(power(x('2'), 2) + 
power(x('1'), 2))) * sqrt(power(x('2'), 2) + 
power(x('1'), 2)))) + 
x('1')) - 
x('3') + 
0.0050000000000000001 * power(x('2'), 2) + 
0.0050000000000000001 * power(x('1'), 2) =l= 0;
con2..((- (sin(sqrt(power(x('2'), 2) + 
power(x('1'), 2))) * sqrt(power(x('2'), 2) + 
power(x('1'), 2)))) + 
x('2')) * ((- (sin(sqrt(power(x('2'), 2) + 
power(x('1'), 2))) * sqrt(power(x('2'), 2) + 
power(x('1'), 2)))) + 
x('2')) - 
x('3') + 
0.0050000000000000001 * power(x('2'), 2) + 
0.0050000000000000001 * power(x('1'), 2) =l= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


