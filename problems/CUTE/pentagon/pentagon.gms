* GAMS-model pentagon.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*12/;
 Set j/1*6/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 1/power(power(x('1') - 
x('2'), 2) + 
power(x('4') - 
x('5'), 2), 8) + 
1/power(power(x('1') - 
x('3'), 2) + 
power(x('4') - 
x('6'), 2), 8) + 
1/power(power(-x('2') + 
x('3'), 2) + 
power(-x('5') + 
x('6'), 2), 8);


con1..0.30901699437494723 * x('3') - 
0.95105651629515364 * x('6') =l= 1;
con2..(-0.80901699437494756) * x('3') - 
0.58778525229247303 * x('6') =l= 1;
con3..(-0.80901699437494734) * x('3') + 
0.58778525229247325 * x('6') =l= 1;
con4..0.30901699437494745 * x('3') + 
0.95105651629515353 * x('6') =l= 1;
con5..0.30901699437494723 * x('2') - 
0.95105651629515364 * x('5') =l= 1;
con6..(-0.80901699437494756) * x('2') - 
0.58778525229247303 * x('5') =l= 1;
con7..(-0.80901699437494734) * x('2') + 
0.58778525229247325 * x('5') =l= 1;
con8..0.30901699437494745 * x('2') + 
0.95105651629515353 * x('5') =l= 1;
con9..0.30901699437494723 * x('1') - 
0.95105651629515364 * x('4') =l= 1;
con10..(-0.80901699437494756) * x('1') - 
0.58778525229247303 * x('4') =l= 1;
con11..(-0.80901699437494734) * x('1') + 
0.58778525229247325 * x('4') =l= 1;
con12..0.30901699437494745 * x('1') + 
0.95105651629515353 * x('4') =l= 1;
x.up('1')=1;
x.up('2')=1;
x.up('3')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


