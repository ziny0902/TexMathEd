//==================================================================================================
// T e x 2 p n g                                                                     Implementation
//                                                                                By Bruno Bachelet
//==================================================================================================
// Copyright (c) 1999-2016
// Bruno Bachelet - bruno@nawouak.net - http://www.nawouak.net
//
// This program is free software; you can redistribute it and/or modify it under the terms of the
// GNU General Public License as published by the Free Software Foundation; either version 2 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
// without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
// the GNU General Public License for more details (http://www.gnu.org).

// This programs allows to convert a LaTeX formula into a PNG image.

// You will need LaTeX, GhostScript and Linux facilities to use this program. The optional
//ugraphical display requires Java classes from the B++ Library.

// Headers //---------------------------------------------------------------------------------------
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>

// Types //-----------------------------------------------------------------------------------------
typedef std::ifstream InputFile;
typedef std::ofstream OutputFile;
typedef std::string   String;

typedef bool          boolean_t;
typedef unsigned char byte_t;
typedef unsigned int  cardinal_t;
typedef char          character_t;
typedef const char *  cstring_t;
typedef long          integer_t;
typedef double        real_t;
typedef char *        string_t;

// Portability //-----------------------------------------------------------------------------------
// #define or  ||
// #define and &&
// #define not !

// Global Variables //------------------------------------------------------------------------------
String    bpp_java       = "";
boolean_t display        = false;
boolean_t lowQuality     = false;
boolean_t percentReplace = false;
boolean_t quiet          = true;
real_t    scale          = 20;
boolean_t secureProgram  = false;
boolean_t starReplace    = false;
String    temporary      = "tex2png";

String auxFile;
String dviFile;
String epsFile;
String logFile;
String pngFile;
String pnmFile;
String psFile;
String outFile;
String texFile;

// Functions Implementation //----------------------------------------------------------------------

//------------------------------------------------------------------------------------------CutImage
void cutImage(cstring_t _inputFile,cstring_t _outputFile) {
 character_t  character;
 InputFile    fin;
 OutputFile   fout;
 boolean_t ** image;
 String       word;

 cardinal_t n1;
 cardinal_t x1;
 cardinal_t y1;

 cardinal_t height;
 cardinal_t left;
 cardinal_t top;
 cardinal_t width;

 cardinal_t border = 4;
 cardinal_t bottom = 0;
 cardinal_t right  = 0;
 cardinal_t x2     = 0;
 cardinal_t y2     = 0;

 // Image Matrix Reading //
 fin.open(_inputFile,std::ios::in|std::ios::binary);
 if (fin.fail()) {
  std::cerr << "[!] Can't read Image Matrix." << std::endl;
  exit(1);
 }
 fin >> word;

 while (not fin.eof() and word!="(device=pnm)") fin >> word;
 if (fin.eof()) return;

 fin >> x1 >> y1;
 image=new boolean_t *[y1];
 image[0]=new boolean_t[x1];

 left=x1-1;
 top=y1-1;
 n1=x1*y1;

 while (n1>0) {
  --n1;

  // Pixel Reading //
  do fin.read(&character,1);
  while ((byte_t)character<=32);

  image[y2][x2]=(character=='1');

  // Bounding Box Computation //
  if (image[y2][x2]) {
   left=std::min(x2,left);
   right=std::max(x2,right);
   top=std::min(y2,top);
   bottom=std::max(y2,bottom);
  }

  // Next Line //
  if (++x2 == x1) {
   x2=0;
   if (++y2 < y1) image[y2]=new boolean_t[x1];
  }
 }

 fin.close();

 // PNM Image Writing //
 fout.open(_outputFile);
 fout << "P1" << std::endl;
 fout << "# Image generated by TeX2PNG" << std::endl;

 height=(bottom-top+1)+2*border;
 width=(right-left+1)+2*border;
 fout << width << " " << height << std::endl;

 // Top Border //
 y2=0;

 while (y2<border) {
  x2=0;
  while (x2++<width) fout << '0';
  fout << std::endl;
  ++y2;
 }

 // Bounded Image //
 y2=0;

 while (y2<y1) {
  if (y2>=top and y2<=bottom) {
   // Left Border //
   x2=0;
   while (x2++ < border) fout << '0';

   // Line //
   x2=left;
   while (x2<=right) fout << (image[y2][x2++] ? '1' : '0');

   // Right Border //
   x2=0;
   while (x2++ < border) fout << '0';

   // End Of Line //
   fout << std::endl;
  }

  delete [] image[y2++];
 }

 delete [] image;

 // Bottom Border //
 y2=0;

 while (y2<border) {
  x2=0;
  while (x2++<width) fout << '0';
  fout << std::endl;
  ++y2;
 }

 // File Closing //
 fout << std::endl;
 fout.close();
}

//------------------------------------------------------------------------------GenerateFormulaImage
void generateFormulaImage(cstring_t _outputFile,cstring_t _formula) {
 String      command;
 InputFile   fin;
 OutputFile  fout;
 cardinal_t  position;
 character_t resolution[32];
 character_t size[32];
 String      word;

 integer_t x1;
 integer_t x2;
 integer_t y1;
 integer_t y2;

 String formula;
 String outputFile;

 // File Name Normalizing //
 while (*_outputFile) {
  if (*_outputFile=='\\') outputFile+='/';
  else outputFile+=*_outputFile;

  ++_outputFile;
 }

 // Formula Construction //
 while (*_formula != 0) {
  if (starReplace and *_formula=='*') formula+="{\\times}";
  else if (secureProgram and *_formula=='"') formula+="";
  else formula+=*_formula;

  ++_formula;
 }

 if (percentReplace) {
  character_t ascii[] = { 0,0 };
  character_t hexa[]  = { '%','0','0',0 };

  while ((byte_t)ascii[0]<255) {
   ++(ascii[0]);

   if (hexa[2]=='9') hexa[2]='A';
   else if (hexa[2]=='F') {
    if (hexa[1]=='9') hexa[1]='A';
    else ++hexa[1];

    hexa[2]='0';
   }
   else ++hexa[2];

   while ((position=formula.find(hexa)) != String::npos) formula.replace(position,3,ascii);
  }
 }

 // LaTeX Generation //
 std::cout << "[>] LaTeX File Generation..." << std::endl;
 fout.open(texFile.c_str(),std::ios::in|std::ios::trunc);

 fout << "\\documentclass[a4paper,11pt]{article}" << std::endl
      << "\\usepackage{amssymb}" << std::endl
      << "\\usepackage{amsmath}" << std::endl
      << "\\usepackage{epsfig}" << std::endl
      << "\\pagestyle{empty}" << std::endl
      << "\\textwidth 10cm" << std::endl
      << "\\setlength{\\parindent}{0mm}" << std::endl
      << "\\begin{document}" << std::endl
      << "$\\displaystyle " << formula << "$" << std::endl
      << "\\end{document}" << std::endl;

 fout.close();

 if (fout.fail()) {
  std::cerr << "[!] Can't create the LaTeX file." << std::endl;
  exit(1);
 }

 // LaTeX Compilation //
 std::cout << "[>] LaTeX File Compilation..." << std::endl;
 command="latex -interaction=nonstopmode "+texFile;
 if (quiet) command+=" > "+outFile+" 2> "+outFile;
 system(command.c_str());
 command="touch "+dviFile;
 system(command.c_str());
 remove(texFile.c_str());
 remove(auxFile.c_str());
 remove(logFile.c_str());

 // EPS Generation //
 std::cout << "[>] PostScript File Generation..." << std::endl;
 command="dvips -q -D 96 -E -n 1 -p 1 -o "+epsFile+" "+dviFile;
 if (quiet) command+=" > "+outFile+" 2> "+outFile;
 system(command.c_str());
 command="touch "+epsFile;
 system(command.c_str());
 remove(dviFile.c_str());

 // Bounding Box Computation //
 fin.open(epsFile.c_str(),std::ios::in);

 do fin >> word;
 while (not fin.eof() and word!="%%BoundingBox:");

 if (word=="%%BoundingBox:") fin >> x1 >> y1 >> x2 >> y2;
 fin.close();

 if (fin.fail()) {
  std::cerr << "[!] Can't find the bounding box." << std::endl;
  exit(1);
 }

 if (secureProgram) {
  if ((x2-x1)*scale*0.25 > 1600 or (y2-y1)*scale*0.25 > 1200) {
   std::cerr << "[!] Sorry, image too big." << std::endl;
   exit(1);
  }
 }

 // PS Generation //
 fout.clear();
 fout.open(psFile.c_str(),std::ios::in|std::ios::trunc);

 fout << "1 1 1 setrgbcolor" << std::endl
      << "newpath" << std::endl
      << "-1 -1 moveto" << std::endl
      << (x2-x1+2) << " -1 lineto" << std::endl
      << (x2-x1+2) << " " << (y2-y1+2) << " lineto" << std::endl
      << "-1 " << (y2-y1+2) << " lineto" << std::endl
      << "closepath" << std::endl
      << "fill" << std::endl
      << -x1 << " " << -y1 << " translate" << std::endl
      << "0 0 0 setrgbcolor" << std::endl
      << "("+epsFile+") run" << std::endl;

 fout.close();

 if (fout.fail()) {
  std::cerr << "[!] Can't generate the PS file." << std::endl;
  exit(1);
 }

 // PNG Generation //
 std::cout << "[>] PNG Image Generation..." << std::endl;

String opaqueOut = outputFile+".opaq";
 if (lowQuality) {
  scale*=0.15;
  sprintf(size,"%dx%d",(int)((x2-x1+5)*scale),(int)((y2-y1)*scale));
  sprintf(resolution,"%dx%d",(int)(scale*62),(int)(scale*62));
  command=String("gs -q -g")+size+" -r"+resolution;
  command+=" -sDEVICE=pnggray -sOutputFile=";
  command+=opaqueOut;
  command+=" -I. -dNOPAUSE -dBATCH -- "+psFile+";";

  if (quiet) command+=" > "+outFile+" 2> "+outFile;
  system(command.c_str());

  command=String("convert ")+opaqueOut+" -transparent white "+outputFile;
  system(command.c_str());

  remove(opaqueOut.c_str());
  remove(epsFile.c_str());
  remove(psFile.c_str());
 }
 else {
  sprintf(size,"%dx%d",(int)((x2-x1+10)*scale),(int)((y2-y1)*scale));
  sprintf(resolution,"%dx%d",(int)(scale*72),(int)(scale*72));
  command=String("gs -q -g")+size+" -r"+resolution;
  command+=" -I. -sDEVICE=pnm -sOutputFile="+pnmFile+" -dNOPAUSE -dBATCH -- "+psFile+";";

  if (quiet) command+=" > "+outFile+" 2> "+outFile;
  system(command.c_str());

  remove(epsFile.c_str());
  remove(psFile.c_str());

  cutImage(pnmFile.c_str(),pnmFile.c_str());

  command="pnmscale 0.25 "+pnmFile+" 2> "+opaqueOut+" | pnmtopng > ";
  command+=opaqueOut;
  if (quiet) command+=" 2> "+opaqueOut;
  system(command.c_str());
  remove(pnmFile.c_str());

  // command=String("convert ")+opaqueOut+" -transparent white "+outputFile;
  // system(command.c_str());
  // remove(opaqueOut.c_str());
 }

 remove(outFile.c_str());

 // Image Display //
 if (display) {
  if (bpp_java=="") {
   if (std::getenv("BPP_JAVA")) bpp_java=String(std::getenv("BPP_JAVA"));
   else bpp_java=".";
  }

  std::cout << "[>] Image Display..." << std::endl;
  command="java -cp \""+bpp_java+"\" bpp.graphic.PictureFrame ";
  command+=outputFile;
  std::cout << command << std::endl;
  system(command.c_str());
  remove(pngFile.c_str());
 }
}

//----------------------------------------------------------------------------------------------Main
int main(int argc,const char * argv[]) {
 String formula;
 String filename;

 int i = 1;

 while (i<argc) {
  if (argv[i][0]=='-') {
   switch (argv[i][1]) {
    case 'b': bpp_java=(argv[i]+2); break;
    case 'r':
     if (argv[i][2]=='*') starReplace=true;
     if (argv[i][2]=='%') percentReplace=true;
    break;
    case 's': scale=atof(argv[i]+2); break;
    case 't': temporary=(argv[i]+2); break;
    case 'v': quiet=false; break;
    case 'd': display=true; break;
    case 'l': if (argv[i][2]=='q') lowQuality=true; break;
    default: std::cout << "[!] Unknown option '" << argv[i] << "'" << std::endl;
   }
  }
  else {
   if (formula=="") formula=argv[i];
   else filename=argv[i];
  }

  ++i;
 }

 if (secureProgram) {
  display=false;
  if (scale>20) scale=20;
 }

 texFile=temporary+".tex";
 outFile=temporary+".out";
 dviFile=temporary+".dvi";
 auxFile=temporary+".aux";
 logFile=temporary+".log";
 epsFile=temporary+".eps";
 psFile=temporary+".ps";
 pnmFile=temporary+".pnm";
 pngFile=temporary+".png";

 if (display and filename=="") filename=pngFile;

 if (formula=="" or (not display and filename=="")) {
  std::cout << "[!] Syntax: " << argv[0] << " [options] <formula> [output file]" << std::endl
            << std::endl
            << "    Options:" << std::endl
            << "      -bx = sets the path of the B++ Library Java classes to x." << std::endl
            << "      -d  = displays the image, the output file is optional." << std::endl
            << "      -lq = low quality, faster." << std::endl
            << "      -r* = replaces the '*' symbol by the '\\times' command." << std::endl
            << "      -r% = replaces the '%XX' hexa sequences by the corresponding ASCII symbol." << std::endl
            << "      -sx = sets the scale of the image to x (real value)." << std::endl
            << "      -tx = sets the prefix of the temporary files." << std::endl
            << "      -v  = verbose mode." << std::endl;

  exit(1);
 }

 generateFormulaImage(filename.c_str(),formula.c_str());
 return 0;
}

// End //-------------------------------------------------------------------------------------------
