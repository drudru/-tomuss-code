doc:
	cd .. ; ./plugins.py
	./generate_doc.py <Welcome.orig.xml >/dev/null
	./generate_doc.py <Welcome.orig.xml >Welcome-local.xml # New TOC
	cd .. ; \
        if [ -d LOCAL.template ] ; \
        then mv LOCAL LOCAL.orig ; \
             mv LOCAL.template LOCAL ; \
             ./plugins.py ; \
             mv LOCAL LOCAL.template ; \
             mv LOCAL.orig LOCAL ; \
        fi
	./generate_doc.py <Welcome.orig.xml >/dev/null
	./generate_doc.py <Welcome.orig.xml >Welcome.xml # New TOC


clean:
	rm -f xxx_*
