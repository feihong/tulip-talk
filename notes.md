What is PEP 3156?
-----------------

- "Asynchronous IO Support Rebooted"
- Describes a new event loop API
- Compatible with current popular event loops (Twisted, Tornado, etc.)
- Should land in the standard library in 3.4 (early 2014)

The big take-away
-----------------

We're going to be able to write asynchronous code without threads or callbacks!

Threads vs event loop
---------------------

- I'm not going to talk about this
- Twisted has thrived for more than a decade
- For a detailed discussion see http://krondo.com/?p=1209

Twisted vs Tulip
----------------

Ugh, how to explain this?

I could just give you a boring list of differences...

Or I could use an analogy...

Programming with Twisted is like...
-----------------------------------

(picture)
Being a mystical ninja warrior!


Mystical Ninja Warrior
----------------------
- Can defeat demons and demigods by deploying an army of shadow clones
- Mental gymnastics required to coordinate shadow clones requires years of brutal training
- Ninja magic always comes with a price -- the more clones you make, the more insane you become


Programming with Tulip is like...
---------------------------------

(picture)
Playing a lot of Plants Vs Zombies

Playing a lot of Plants Vs Zombies
----------------------------------
- Can defeat the zombie horde by aggressive use of horticulture
- Must be skilled in the art of rapidly and precisely tapping on glass
- Somehow end up playing for hours without eating or sleeping

Alrighty
--------

With the analogies out of the way, let's look at some examples.

Fetching a web page in Twisted
-------------------------------
(example)

note: There are a total of 5 callback functions in this example.
I know that if I just used twisted.web.client.getPage(), the example would be a lot simpler. But for this example I wanted to print out the response headers, and getPage() does not provide access to them.

Control flow diagram
--------------------

Look at krondo.com for some examples of how to draw this

Overview of problems in callback-based asynchronous programming
---------------------------------------------------------------
tbd

Fetching a web page in Tulip
----------------------------
(example)

Fetching a web page in Tulip w/ callbacks
-----------------------------------------
(example)

note: This example is actually less readable than the Twisted example, despite the fact that both examples use callbacks. Since callbacks in Tulip are not chained, you have to invoke the next callback from within the previous callback. Therefore you must read every single callback function to understand the control flow of the entire program. Baaaaaaaaaaaaaaaaarrrrrrf.

note: It's clear that Tulip's callback-based API is a lot weaker than Twisted's. This is almost certainly intentional on Guido's part.

Add a note about error callback readability.

Fetching a web page in Twisted w/ inline callbacks
--------------------------------------------------
(example)

note: You can write quite a lot of Twisted code without explicitly using callbacks, but notice that even in this simple example we could not avoid defining the dataReceived and connectionLost callback methods. Callbacks are intrinsic to the Twisted API!

The Tulip API
-------------
- Basics are documented in PEP 3156
- Probabaly alpha quality, prone to changes, not available in package index
- Includes low-level stuff like sockets, file I/O
- Includes HTTP (with support for websockets)

Coroutines vs tasks
-------------------
- To me, the most confusing thing about Tulip.
- Coroutines need to be invoked using "yield from"
- Tasks can be invoked like a normal function

Coroutine
---------

Basically a function that contains at least one "yield from" statement

@tulip.coroutine
def download(url):
    response = yield from tulip.http.request('GET', url)
    return yield from response.read()

Calling "download()" returns a generator, but otherwise does nothing! You need to do "yield from download()" to run the body of a coroutine.

note: The tulip.coroutine decorator actually doesn't do anything. It exists to help you mark your coroutine functions as such.

Task
----

A task is also a function, but it wraps around a coroutine.

@tulip.task
def download(url):
    response = yield from tulip.http.request('GET', url)
    return yield from response.read()

Calling "download()" actually does run the body of the function. The "yield from" part is done implicitly for you.

note: Tulip's Task class has a similar API to Twisted's Deferred class.

Why bother to use tasks?
------------------------

- To interoperate with callback-based frameworks
- To gain the ability to cancel long-running operations
- "Interoperating between coroutines" (I don't fully understand this yet)

Note:
My impression is that you should generally prefer coroutines over tasks. Using "yield from" is the most direct way of getting the return value of a coroutine. According to PEP 3156, switching to a coroutine is faster than switching to a task.

Here's an example of when you have to use a task. If you are writing a coroutine that you know has a chance of being prematurely terminated and you have a particular operation that you really want to be done, you can execute it inside a task instead of using yield from.


Web programming using Tulip
---------------------------

- All the classes you need are in the tulip.http module
- Make subclass of tulip.http.ServerHttpProtocol
- Override the handle_request() method

Hello World!
------------
(example)

Some observations
-----------------

The HTTP API is fairly simple, but a bit low level for everyday web programming.

Expect a thousand microframeworks to bloom in the near future.

Speaking of microframeworks...

Introducing Viol
----------------
- Very tiny web framework based on Tulip
- After initial page load, messages between client and server are exchanged via websockets
- Makes code demos a bit more visual

Tulip API demos
---------------

Now for a bunch of demos...


Tulip API demos
---------------

(Picture: Save me, Jebus!)


Two coroutines, serial
----------------------

Note: In viol, add the ability to use a custom Writer class.
Note: Make sure foo() and bar() have return values, perhaps stating the number of widgets created and how long it took.

Two coroutines, simultaneous
----------------------------

Wait for both coroutines to finish
----------------------------------

Loop through coroutine results in order of finishing
----------------------------------------------------

Execute synchronous code in another thread
------------------------------------------


A regex tool
------------


Chat application
----------------











