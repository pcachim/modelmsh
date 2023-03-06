//+
Show {
  Curve{1}; 
}
//+
Rectangle(1) = {-1, 0, 0, 1, 0.5, 0};
//+
SetFactory("Built-in");
//+
SetFactory("OpenCASCADE");
//+
Rectangle(1) = {-0.5, -0.1, -0.7, 1, 0.5, 0};
//+
Rectangle(2) = {0, 0.2, -0.6, 1, 0.5, 0};
//+
Show "*";
//+
Compound Surface {1};
//+
Transfinite Surface {1};
