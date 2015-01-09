all: butterflynet.png logo.png favicon.ico

butterflynet.png:butterflynet.svg
	inkscape --export-png=$@ --export-area-drawing --export-width=32 $?

logo.png:logo.svg
	inkscape --export-png=$@ --export-width=114 $?

favicon.ico:logo.png
	convert logo.png -resize 16x16 $@

clean:
	# Nothing to do ?
