---
title: 'Streamz: A small library to manage continuous streams of data'
tags:
  - Stream
  - Dask
authors:
 - name: Matthew Rocklin
   orcid: ?
   affiliation: 1
 - name: Christopher J. Wright
   orcid: 0000-0003-2522-7028
   affiliation: 2
 - name: Julien Lhermitte
   orcid: 0000-0003-0660-975X
   affiliation: 5
 - name: Daniel B. Allan
   orcid: 0000-0002-5947-6017
   affiliation: 4
 - name: Stuart I. Campbell
   orcid: 0000-0001-7079-0878
   affiliation: 4
 - name: Kevin G. Yager
   orcid: 0000-0001-7745-2513
   affiliation: 5
 - name: Simon J. L. Billinge
   orcid: 0000-0002-9734-4998
   affiliation: 2, 3
affiliations:
 - name: Anaconda Inc.
   index: 1
 - name: Department of Applied Physics and Applied Mathematics, Columbia University
   index: 2
 - name: Condensed Matter Physics and Materials Science Department, Brookhaven National Laboratory
   index: 3
 - name: NSLS-II, Brookhaven National Laboratory
   index: 4
 - name: Center for Functional Nanomaterials, Brookhaven National Laboratory
   index: 5
date: 19 September 2017
bibliography: paper.bib
---

# Summary

- This is a small library to manage continuous streams of data, particularly when complex branching and control flow situations arise. 
- This provides a framework for streaming data analysis in pure Python with hooks into the Dask task scheduler for automatic parallelization.
- Streamz is similar to reactive
programming systems like [RxPY](https://github.com/ReactiveX/RxPY) or big
data streaming systems like [Apache Flink](https://flink.apache.org), [Apache Beam](https://beam.apache.org/get-started/quickstart-py) or [Apache Spark Streaming](https://spark.apache.org/streaming/).
- This software forms the backbone for data processing at the NSLS-II X-ray powder diffraction and complex materials scattering data analysis pipelines.

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

# References

# Acknowledgments
Software and writing contributions from Wright and Billinge were supported by the U.S. National Science Foundation through
grant DMREF-1534910
This research used resources of the Center for Functional Nanomaterials and the NSLS-II, which is a U.S. DOE Office of Science Facility, at Brookhaven National Laboratory under Contract No. DE-SC0012704