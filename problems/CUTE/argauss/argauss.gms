* GAMS-model argauss.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*15/;
 Set j/1*3/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1.. exp((-0.5) * x('2') * power(((- x('3'))) + 3.5, 2)) * x('1') =e= 0.00089999999999999998;
con2.. exp((-0.5) * x('2') * power(((- x('3'))) + 3, 2)) * x('1') =e= 0.0044000000000000003;
con3.. exp((-0.5) * x('2') * power(((- x('3'))) - 3.5, 2)) * x('1') =e= 0.00089999999999999998;
con4.. exp((-0.5) * x('2') * power(((- x('3'))) - 3, 2)) * x('1') =e= 0.0044000000000000003;
con5.. exp((-0.5) * x('2') * power(((- x('3'))) + 2.5, 2)) * x('1') =e= 0.017500000000000002;
con6.. exp((-0.5) * x('2') * power(((- x('3'))) - 2.5, 2)) * x('1') =e= 0.017500000000000002;
con7.. exp((-0.5) * x('2') * power(((- x('3'))) + 2, 2)) * x('1') =e= 0.053999999999999999;
con8.. exp((-0.5) * x('2') * power(((- x('3'))) - 2, 2)) * x('1') =e= 0.053999999999999999;
con9.. exp((-0.5) * x('2') * power(((- x('3'))) - 1.5, 2)) * x('1') =e= 0.1295;
con10.. exp((-0.5) * x('2') * power(((- x('3'))) + 1.5, 2)) * x('1') =e= 0.1295;
con11.. exp((-0.5) * x('2') * power(((- x('3'))) - 1, 2)) * x('1') =e= 0.24199999999999999;
con12.. exp((-0.5) * x('2') * power(((- x('3'))) + 1, 2)) * x('1') =e= 0.24199999999999999;
con13.. exp((-0.5) * x('2') * power(((- x('3'))) - 0.5, 2)) * x('1') =e= 0.35210000000000002;
con14.. exp((-0.5) * x('2') * power((- x('3')), 2)) * x('1') =e= 0.39889999999999998;
con15.. exp((-0.5) * x('2') * power(((- x('3'))) + 0.5, 2)) * x('1') =e= 0.35210000000000002;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


