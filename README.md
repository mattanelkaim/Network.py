<h1> Network.py Course - Socket Programming </h1>
<p> Acquiring experience on working with TCP and UDP sockets, using Python's <em>socket</em> module.</p>

---

<h2> Key Exercises </h2>
<ul>
    <li>
        <strong><a href="https://github.com/mattanelkaim/Network.py/tree/master/Ex2.5.1">2.5.1</a></strong> - Implementing a simple <strong>echo server</strong>.
    </li>
    <li>
        <strong><a href="https://github.com/mattanelkaim/Network.py/tree/master/Ex2.5.2">2.5.2</a></strong> - Adding <strong>more commands</strong> to the server, making it more <strong>dynamic</strong> for the client.
    </li>
    <li>
        <strong><a href="https://github.com/mattanelkaim/Network.py/tree/master/Ex3.5.2">3.5.2</a></strong> - Implememting <strong>time-outs and retransmissions</strong> for a client in a UDP socket.
    </li>
    <li>
        <strong><a href="https://github.com/mattanelkaim/Network.py/tree/master/Ex4.3">4.3</a></strong> - Handling <strong>multiple client TCP connections</strong> simultaneously with the <em>select</em> module.
    </li>
    <li>
        <strong><a href="https://github.com/mattanelkaim/Network.py/tree/master/TRIVIA%20GAME">TRIVIA GAME</a> - Summary project</strong>. Creating the <strong><em>chatlib</em> protocol</strong>, that enables to transfer commands & data between clients and the server.
        <br>
        Developing a <strong>robust server-client system</strong> that allows hosting and participation in the game.
        <br>
        Also experimenting with <strong>some modules</strong>, such as:
        <br>
        <ul>
            <li><em>requests</em> - <strong>get data from a web service</strong></li>
            <li><em>json</em> - organize the server data</li>
            <li><em>hashlib</em> - create unique question IDs</li>
            <li><em>select</em> - <strong>handle multiple TCP clients</strong></li>
            <li><em>logging</em> - log debugging info</li>
        </ul>
        <br>
        The trivia server scans client connections only <strong>within its subnet</strong>.
    </li>
</ul>

---

<h2>Instructions -Trivia Game</h2>
<ol>
    <li>Use <em>ipconfig</em> in the server's machine and assign the IP to the <strong><em>SERVER_IP</em> variable</strong>.</li>
    <li>In the client file*, provide the <strong>IP address</strong> of the server (which is located in the <strong>same subnet)</strong>.</li>
    <li><strong>Run</strong> the server file.</li>
    <li>Run as many clients as you want, <strong>play the game</strong> and show off your knowledge in computer science!</li>
</ol>
<p>* You can then compile the client file with the <em>compile_client.bat</em> script.</p>
