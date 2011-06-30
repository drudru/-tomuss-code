/*

This program connects to the indicated X11 server
and accept the following commands (ended by a \n) :

* 'quit'           : terminates the process
* 'snapshot'       : takes a screen snapshot
* 'analyse'        : List of found images in the snapshot on stdout
                     Image with name beginning by '_' are not merged
* 'diff [filename]': Write the number of bytes change between the two last
                     snapshots on stdout.
		     If a filename if provided, then it is the difference
		     between the last snapshot and the filename.
* 'save <filename>': dump the current snapshot in the file (- is PPM stdout)
* 'find <charname>': -1: unknown char, 0 not found, 1 found in current snap.
                     The char images are in the 'D' directory.
* 'subtract <filename>': Store the last diff computed in the file
                         (- is PPM stdout)

The image filename define the format.
If it is 'stdout' the image is PPM

The searched images (chars) are stored in 'D' directory.

*/

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <dirent.h>

typedef unsigned char Pixel[3] ;

typedef struct image {
  char *charname ;
  int width, height ;
  Pixel **image ;
  struct image *next ;
  struct image *all ;
} Image ;

typedef struct {
  int x, y, w, h, d ;
  char *text ;
} Rect ;

static Image **chars ;

#define MALLOC(X,N) do { X = calloc(sizeof(*X), N) ; assert(X) ; } while(0)
#define LINE_SPACING 8
#define CHAR_SPACING 5

/******************************************************************************
 * Reading a PPM file
 *****************************************************************************/

char * get_line(FILE *f)
{
  static char buffer[1024] ;
  char *err ;

  buffer[0] = '\0' ;
  do
    {
      err = fgets(buffer, sizeof(buffer), f) ;
    }
  while( buffer[0] == '#' ) ;
  
  return buffer ;
}

Image *alloc(width, height)
{
  Image *image ;
  int i ;

  MALLOC(image, 1) ;
  image->height = height ;
  image->width = width ;
  MALLOC(image->image, image->height) ;
  for(i=0; i<image->height; i++)
    MALLOC(image->image[i], image->width) ;

  return image ;
}

void free_image(Image *image)
{
  int i ;
  for(i=0; i<image->height; i++)
    free(image->image[i]) ;
  free(image->image) ;
  free(image) ;
}

int get_index(Pixel p)
{
  return ((unsigned int)p[0] << 16)
    | ((unsigned int)p[1] << 8)
    | (unsigned int)p[2] ;
}

Image *from_file(FILE *f)
{
  char *buffer ;
  Image *image ;
  int x, y ;

  buffer = get_line(f) ;
  if ( strcmp(buffer, "P6\n") != 0 )
    return NULL ;

  buffer = get_line(f) ;
  sscanf(buffer, "%d%d", &x, &y) ;
  image = alloc(x, y) ;

  buffer = get_line(f) ;
  assert(strcmp(buffer, "255\n") == 0 ) ;

  for(y=0; y<image->height; y++)
    if ( fread(image->image[y], 1, 3*image->width, f) != 3*image->width )
      exit(1) ;

  return image ;
}

Image *load_file(char *filename)
{
  FILE *f ;
  Image *image ;

  if ( strcmp(filename + strlen(filename) - 4, ".ppm") == 0 )
    {
      f = fopen(filename, "r") ;
      image = from_file(f) ;
      fclose(f) ;
    }
  else
    {
      char command[999] ;
      sprintf(command, "convert %s ppm:-", filename) ;
      f = popen(command, "r") ;
      image = from_file(f) ;
      pclose(f) ;
    }

  return image ;
}

/******************************************************************************
 * Write a PPM file
 *****************************************************************************/

void to_file(Image *image, FILE *f)
{
  int y ;

  fprintf(f, "P6\n%d %d\n255\n", image->width, image->height) ;
  for(y=0; y<image->height; y++)
    if ( fwrite(image->image[y], 1, 3*image->width, f) != 3*image->width )
	exit(1) ;
}

void display(Image *image, char *filename)
{
  if ( strcmp(filename, "-") == 0 )
    to_file(image, stdout) ;
  else
    {
      char cmd[999] ;
      FILE *f ;
      sprintf(cmd, "convert ppm:- %s", filename) ;
      f = popen(cmd, "w") ;
      to_file(image, f) ;
      pclose(f) ;
    }
}

/******************************************************************************
 * X11 dumper.
 *****************************************************************************/

static char *display_name ;

Image *get_image(Image *old)
{
  static Display *dpy = NULL ;
  static Window w ;
  static int width, height, size ;
  static XWindowAttributes win_info ;
  Image *image ;
  XImage *image_x ;
  int x, y ;
  char *p ;

  if ( dpy == NULL )
    {
      dpy = XOpenDisplay(display_name) ;
      w = RootWindow(dpy, 0) ;

      XGetWindowAttributes(dpy, w, &win_info) ;

      width = win_info.width;
      height = win_info.height;

      size = width * height * 4 ;
    }

  if ( old )
    image = old ;
  else
    image = alloc(width, height) ;
  image_x = XGetImage(dpy, w, 0, 0, width, height, AllPlanes, ZPixmap);
  
  p = image_x->data ;
  for(y=0; y<image->height; y++)
    for(x=0; x<image->width; x++)
      {
	image->image[y][x][0] = p[2] ;
	image->image[y][x][1] = p[1] ;
	image->image[y][x][2] = p[0] ;
	p += 4 ;
      }

  XDestroyImage(image_x) ;

  return image ;
}

/******************************************************************************
 * Differences count
 *****************************************************************************/

int nr_diff(Image *a, Image*b)
{
  int x, y, n ;

  n = 0 ;
  for(y=0; y<a->height; y++)
    for(x=0; x<a->width*3; x++)
      n += a->image[y][0][x] != b->image[y][0][x] ;

  return n ;
}

/******************************************************************************
 * Subtract image
 *****************************************************************************/

Image* subtract(Image *a, Image*b)
{
  int x, y ;
  Image *s ;

  s = alloc(a->width, a->height) ;
  
  for(y=0; y<a->height; y++)
    for(x=0; x<a->width*3; x++)
      if ( a->image[y][0][x] == b->image[y][0][x] )
	s->image[y][0][x] = a->image[y][0][x] / 4 ;
      else
	s->image[y][0][x] = 128 + (a->image[y][0][x] | b->image[y][0][x])/2 ;

  return s ;
}

/******************************************************************************
 * Searching images in picture
 *****************************************************************************/

int equal(Image *stack, Image *needle, int x, int y)
{
  int yy ;

  if ( stack->width < x + needle->width )
    return 0 ;
  if ( stack->height < y + needle->height )
    return 0 ;

  for(yy=0; yy<needle->height; yy++)
    {
      if ( memcmp(&needle->image[yy][0][0],
		  &stack->image[yy+y][x][0],
		  3*needle->width) != 0 )
	return 0 ;
    }
  return 1 ;
}

int cmp(const void *a, const void *b)
{
  const Rect *aa = a, *bb = b ;
  return aa->x - bb->x ;
}

int merge(Rect *rect, int nr_rect, int *to_concat, int *line_start, int y)
{
  int x_max, i, j ;

  // First character on a new line
  // Sort from left to right on the line
  qsort(&rect[*to_concat], nr_rect - *to_concat - 1, sizeof(rect[0]), cmp) ;
  // fprintf(stderr,"Before: ") ; for(i=*to_concat; i < nr_rect-1; i++) fprintf(stderr,"[%s]",rect[i].text) ; fprintf(stderr,"\n") ;
  for(i=*to_concat; i < nr_rect-1; i++)
    {
      char tmp[1000], *pc ;
      x_max = 0 ;
      pc = tmp ;
      pc += sprintf(pc, "%s", rect[i].text) ;
      if ( rect[i].text[0] != '_' )
	for(j = i+1; j < nr_rect-1; j++)
	  {
	    if ( rect[j].text[0] != '_' && rect[j].x -(rect[j-1].x+rect[j-1].w) < CHAR_SPACING)
	      {
		pc += sprintf(pc, "%s", rect[j].text) ;
		if ( rect[j].x + rect[j].w > x_max )
		  x_max = rect[j].x + rect[j].w ;
		
	      }
	    else
	      break ;
	  }
      else
	j = i+1 ;
      free(rect[i].text) ;
      rect[i].text = strdup(tmp) ;
      // printf("Joined: %s\n", rect[i].text) ;
      memmove(&rect[i+1], &rect[j],
	      (nr_rect - (j-1)) * sizeof(rect[0])) ;
      nr_rect -= j - i - 1 ;
      rect[i].y = *line_start ;
      if ( x_max )
	rect[i].w = x_max - rect[i].x ;
    }
  // fprintf(stderr,"After: ") ; for(i=*to_concat; i < nr_rect-1; i++) fprintf(stderr,"[%s]",rect[i].text) ; fprintf(stderr,"\n") ;
  *to_concat = nr_rect - 1 ;
  *line_start = y ;

  return nr_rect ;
}

Rect* ocr(Image *stack)
{
  static Rect rect[10000] = {{0}} ;
  int nr_rect ;
  int y, x, next_y, next_x;
  int line_start = -100 ;
  int to_concat = 0 ;
  int found_one, index ;
  Image *needle ;

  nr_rect = 0 ;
  for(y=0; y<stack->height-2; y = next_y)
    {
      next_y = y + 1 ;
      
      for(x=0; x<stack->width-2; x = next_x)
	{
	  found_one = 0 ;
	  next_x = x + 1 ;

	  index = get_index(stack->image[y][x]) ^ get_index(stack->image[y+1][x+1])/2 ^ get_index(stack->image[y+2][x+2])/4  ;
	  
	  for(needle = chars[index]; needle; needle = needle->next)
	    {
	      if ( equal(stack, needle, x, y) )
		{
		  found_one = 1 ;
		  rect[nr_rect].x = x ;
		  rect[nr_rect].y = y ;
		  rect[nr_rect].w = needle->width ;
		  rect[nr_rect].h = needle->height ;
		  rect[nr_rect].text = strdup(needle->charname) ;
		  nr_rect++ ;
		  next_x = x + needle->width - 2 ;
		  break ;
		}
	    }
	  if ( found_one && y - line_start > LINE_SPACING )
	    nr_rect = merge(rect, nr_rect, &to_concat, &line_start, y) ;
	}
    }
  nr_rect = merge(rect, nr_rect+1, &to_concat, &line_start, y) ;
  rect[nr_rect].w = 0 ;

  return rect ;
}

int find(Image *stack, Image *needle)
{
  int x, y ;

  for(y=0; y<stack->height-needle->height+1; y++)
    for(x=0; x<stack->width-needle->width+1; x++)
      if ( equal(stack, needle, x, y) )
	return 1 ;

  return 0 ;
}

/******************************************************************************
 * Read the pictures to be searched
 *****************************************************************************/


int filter(const struct dirent *f)
{
  return f->d_name[0] != '.' ;
}

Image* read_chars()
{
  struct dirent **namelist ;
  int i, n, index ;
  char name[999] ;
  Image *image, *first ;
  
  n = scandir("D", &namelist, filter, NULL) ;

  first = NULL ;
  for(i=0;i<n;i++)
    {
      sprintf(name, "D/%s", namelist[i]->d_name) ;
      image = load_file(name) ;
      image->charname = namelist[i]->d_name ;
      image->charname[strlen(image->charname)-4] = '\0' ;

      index = get_index(image->image[0][0]) ^ get_index(image->image[1][1])/2 ^ get_index(image->image[2][2])/4 ;

      if ( chars[index] )
	  image->next = chars[index] ;
      chars[index] = image ;

      image->all = first ;
      first = image ;
    }
  return first ;
}

/******************************************************************************
 * Command interpreter
 *****************************************************************************/


int main(int argc, char **argv)
{
  char command[999], *parameter, filename[999] = "" ;
  Image *current, *previous, *first, *image = NULL, *diff_image = NULL ;

  if ( argc != 2 )
    {
      fprintf(stderr,
	      "Give the X11 display as parameter (for example: ':1')\n") ;
      exit(1) ;
    }
  display_name = argv[1] ;

  MALLOC(chars, 256*256*256) ; // Images to search (hash table)

  first = read_chars() ;
  previous = get_image(NULL) ;
  current = get_image(NULL) ;

  for(;;)
    {
      fflush(stdout) ;
      if ( fgets(command, sizeof(command), stdin) != command )
	break ;
      command[strlen(command)-1] = '\0' ;
      parameter = command + strcspn(command, " ") + 1 ;
      if ( parameter[-1] == '\0' )
	parameter = NULL ;
      else
	parameter[-1] = '\0' ;

      if ( strcmp(command, "quit") == 0 )
	exit(0) ;
      else if ( strcmp(command, "snapshot") == 0 )
	{
	  Image *tmp ;
	  tmp = get_image(previous) ;
	  previous = current ;
	  current = tmp ;
	  continue ;
	}
      else if ( strcmp(command, "diff") == 0 )
	{
	  if ( parameter )
	    {
	      if ( strcmp(filename, parameter) != 0 )
		{
		  if ( image )
		    free_image(image) ;
		  image = load_file(parameter) ;
		  strcpy(filename, parameter) ;
		}
	      diff_image = image ;
	    }
	  else
	    diff_image = previous ;

	  printf("%d\n", nr_diff(current, diff_image)) ;
	  continue ;
	}
      else if ( strcmp(command, "subtract") == 0 )
	{
	  Image *s ;
	  s = subtract(current, diff_image) ;
	  display(s, parameter) ;
	  free_image(s) ;
	}
      else if ( strcmp(command, "find") == 0 )
	{
	  Image *needle ;	  
	  for(needle=first; needle; needle = needle->all)
	    if ( strcmp(parameter, needle->charname) == 0 )
	      {
		printf("%d\n", find(current, needle) ) ;
		break ;
	      }
	  if ( needle == NULL )
	    printf("-1\n") ;
	  continue ;
	}
      else if ( strcmp(command, "save") == 0 )
	{
	  display(current, parameter) ;
	  continue ;
	}
      else if ( strcmp(command, "analyse") == 0 )
	{
	  Rect *r ;
	  int i ;

	  r = ocr(current) ;
	  printf("Rects(") ;
	  for(i=0;r[i].w;i++)
	    printf("(%d,%d,%d,%d,'%s'),", r[i].x, r[i].y, r[i].w, r[i].h,
		   r[i].text) ;
	  printf(")\n") ;
	  continue ;
	}
    }

  return 0 ;
}
