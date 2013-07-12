Asynchronous I/O in Python 3
============================

<div meta>
Feihong Hsu
Chicago Python User Group
July 11, 2013
</div>

What is PEP 3156?
-----------------

- "Asynchronous IO Support Rebooted"
- Describes a new event loop API
- Aims to be compatible with current popular event loops (Twisted, Tornado, etc.)
- Should land in the standard library in 3.4 (early 2014)

The big take-away
-----------------

We're going to be able to write asynchronous code without threads or callbacks!

Threads vs event loop
---------------------
- I'm not going to talk about this
- Twisted being around for more than a decade kinda validates the event loop model
- For a detailed discussion see [An Intro to Asynchronous Programming and Twisted](http://krondo.com/?p=1209)

Twisted vs Tulip
----------------
Ugh, how to explain this?

I could just give you a boring list of differences...

Or I could use an analogy...

Programming with Twisted is like...
-----------------------------------

<div center>
	<img src="ninja_gaiden_2.jpg" height="310px">
	<img src="ninja_gaiden_2.jpg" height="320px">
	<img src="ninja_gaiden_2.jpg" height="330px">
	<br>
	Being a mystical ninja warrior!
</div>


Mystical Ninja Warrior
----------------------
- Can defeat demons and demigods by deploying an army of shadow clones
- Mental gymnastics required to coordinate shadow clones requires years of brutal training
- Ninja magic comes with a terrible price - the more clones you make, the more insane you become


Programming with Tulip is like...
---------------------------------

<div center>
	<img src="plants_vs_zombies.jpg" height="340">
	<br>
	Playing Plants Vs Zombies
</div>

Playing Plants Vs Zombies
-------------------------
- Can defeat a zombie horde by deploying and managing a large number of horticultural specimens
- Not particularly mentally taxing
- Somehow end up playing for hours without eating or sleeping

Alrighty
--------

With the analogies out of the way, let's look at some examples.

Fetching a web page in Twisted
-------------------------------

<div code="examples/1-twisted-download.py"></div>

Notes
-----

There are a total of 5 callbacks in this example.

I know that if I just used twisted.web.client.getPage(), the example would be a lot simpler. But for this example I wanted to print out the response headers, and getPage() does not provide access to them.

Control flow diagram
--------------------
I was going to draw this but then I got sleepy.

Problems with callback-based asynch code
----------------------------------------

- Can be hard to understand control flow
- Error messages are not friendly
- Debugging is harder

Fetching a web page in Tulip
----------------------------

<div code="examples/2-tulip-download.py"></div>

Fetching a web page in Tulip w/ callbacks
-----------------------------------------

<div code="examples/3-tulip-download-callbacks.py"></div>

Notes
-----

This example is actually less readable than the Twisted example, despite the fact that both examples use callbacks. Since callbacks in Tulip are not chained, you have to invoke the next callback from within the previous callback. Therefore you must read every single callback function to understand the control flow of the entire program. Baaaarf.

It's clear that Tulip's callback-based API is more robust than Twisted's. This is probably intentional on Guido's part. He doesn't want you to use callbacks.

Fetching a web page in Twisted w/ inline callbacks
--------------------------------------------------
<div code="examples/4-twisted-download-inline-callbacks.py"></div>

Notes
-----
You can write quite a lot of Twisted code without explicitly using callbacks, but notice that even in this simple example we could not avoid defining the dataReceived and connectionLost callback methods. Callbacks are intrinsic to the Twisted API!

The Tulip API
-------------
- Basics are documented in PEP 3156
- Not available in Python Package Index
- Includes sockets, file I/O, etc.
- Includes concurrency data structures like locks, queues, semaphores
- Includes SSL and HTTP (with support for websockets!)

Notes
-----
Tulip is still prone to changes and possibly still alpha quality. You can browse the source or download it from [Google Code](https://code.google.com/p/tulip/).

Coroutines vs tasks
-------------------
When I first started, the most confusing thing about Tulip.

Coroutines are executed by "yield from".

Tasks are not executed by "yield from".

Coroutine
---------

- Basically a function that contains at least one "yield from" statement.
- Not the same thing as a generator function, which is a function that contains a yield expression.
- Tulip will barf if you try to make it execute a generator.

Coroutine
---------
	
	@tulip.coroutine
	def download(url):
	    response = yield from tulip.http.request('GET', url)
	    return yield from response.read()

Calling "download()" returns a generator object, but otherwise does nothing! You need to do "yield from download()" to run the body of a coroutine.

Notes
-----
The tulip.coroutine decorator actually doesn't do anything. It exists to help you mark your coroutine functions as such.

Task
----

- An object that manages a coroutine
- Roughly equivalent to the Deferred object in Twisted

Task
----

	@tulip.task
	def download(url):
	    response = yield from tulip.http.request('GET', url)
	    return yield from response.read()

Calling "download()" actually does run the body of the function. The "yield from" part is done implicitly for you.

Task
----

In Tulip, there are two ways of creating tasks:

- tulip.task is a decorator that produces a task-wrapping function
- tulip.Task is a constructor that accepts a coroutine

Why bother to use tasks?
------------------------
- To interoperate with callback-based frameworks like Twisted
- To cancel an already-running coroutine
- To start a new coroutine from within another coroutine

Notes
-----
My impression is that you should generally prefer coroutines over tasks. Using "yield from" is the most direct way of getting the return value of a coroutine. According to PEP 3156, switching to a coroutine is faster than switching to a task.

In Tulip, there is a Handle object that is expressly designed for cancelling coroutines, which is returned by the call_soon(), call_later(), and call_at() functions. In some cases it might be better to use a Handle rather than a Task for cancelling a coroutine.

Here's an example of when you have to use a task. If you have a coroutine that you know has a chance of being prematurely terminated and you want to make sure that certain cleanup operations are performed, you might need to execute the cleanup inside a task. Because subsequent calls to yield from inside the coroutine will not be executed.

Wait, so what's a Future?
-------------------------
PEP 3156 makes frequent mention of Futures. 

But talking about Futures is a little confusing, since there are two Future classes: tulip.Future and concurrent.futures.Future.

Notes
-----
The concurrent.futures.Future class is specified in PEP 3148. 

Future is the superclass of Task
--------------------------------
- Future don't necessarily manage a coroutine
- In practice you never create Future objects, only Task objects
- Futures are acceptable to yield from expressions

Methods on Future
-----------------
- cancel()
- cancelled()
- running()
- done()
- result()
- add_done_callback()
- remove_done_callback()
- set_result()
- ...

Web development with Tulip
--------------------------
- All the classes you need are in the tulip.http module
- Make subclass of tulip.http.ServerHttpProtocol
- Override the handle_request() method

Hello World!
------------
<div code="examples/5-hello-world-http.py"></div>

Some observations
-----------------

The HTTP API is fairly simple, but a bit low level for everyday web programming.

Expect a thousand microframeworks to bloom in the near future.

Speaking of microframeworks...

Introducing viol
----------------
- Tiny web framework based on Tulip
- After initial page load, messages between client and server are exchanged via websockets
- Makes code demos a bit more visual

Tulip API demos
---------------

Now for a bunch of demos...


Tulip API demos
---------------
<div>
	<center>
		<img src="save_me_jebus.gif" height="450px">
	</center>
</div>


Serial
------
<div demo="demos/1-serial"></div>

Simultaneous
------------
<div demo="demos/2-simultaneous"></div>

Notes
-----
This demo does demonstrate how to use Task objects, but the actual usage here is an antipattern. The correct way to run two coroutines at the same time is shown in the next demo.

Wait for both coroutines to finish
----------------------------------
<div demo="demos/3-wait"></div>

Loop through coroutine results in order of finishing
----------------------------------------------------
<div demo="demos/4-as_completed"></div>

Execute synchronous code in another thread
------------------------------------------
<div demo="demos/5-run_in_executor"></div>

Talk to event loop from another thread
--------------------------------------
<div demo="demos/6-call_soon_threadsafe"></div>

A regex debugging tool
----------------------
<div demo="demos/7-regex"></div>

Chat application
----------------
<div demo="demos/8-chat"></div>

Links
-----
- [PEP 3156](http://www.python.org/dev/peps/pep-3156/)
- [Guido's PyCon 2013 keynote](http://pyvideo.org/video/1667/keynote-1)
- [An Introduction to Asynchronous Programming and Twisted](http://krondo.com/?page_id=1327)
- [Tulip project page on GoogleCode](https://code.google.com/p/tulip/)
- [Code for this talk on Github](https://github.com/feihong/tulip-talk)
- [Viol project page on Github](https://github.com/feihong/viol)

Questions?
----------
<div center>
	<img src="frosting.png" height="480px">
</div>
