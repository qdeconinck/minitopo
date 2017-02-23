import java.io.*;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.Socket;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;
import java.util.Collections;

public class SiriClient {

    private String serverMessage;

    /* Client parameters */
    public final String SERVERIP; //your computer IP address
    public final int SERVERPORT;
    public final int RUN_TIME; // In seconds
    public final int QUERY_SIZE;
    public final int RESPONSE_SIZE;
    public final int DELAY_QUERY_RESPONSE;
    public final int MIN_PAYLOAD_SIZE;
    public final int MAX_PAYLOAD_SIZE;
    public final int INTERVAL_TIME_MS;
    public final int BUFFER_SIZE;
    public final int BURST_SIZE;
    public final int INTERVAL_BURST_TIME_MS;

    private boolean mRun = false;
    private int messageId = 0;
    private static final int MAX_ID = 100;

    private Random random;
    private long[] sentTime;
    private List<Long> delayTime;
    private String mac;
    private int counter;
    private int missed;
    PrintWriter out;
    BufferedReader in;
    OutputStream outputStream;
    OutputStreamWriter osw;
    Socket socket;
    private int pktCounter;

    /**
     *  Constructor of the class. OnMessagedReceived listens for the messages received from server
     */
    public SiriClient(String serverIp, int serverPort, int runTime, int querySize, int responseSize,
    				  int delayQueryResponse, int minPayloadSize, int maxPayloadSize, int intervalTimeMs,
    				  int bufferSize, int burstSize, int intervalBurstTimeMs) {
        random = new Random();
        sentTime = new long[MAX_ID];
        delayTime = new ArrayList<>();
        counter = 0;
        missed = 0;
        pktCounter = 0;
        /* Client parameters */
        SERVERIP = serverIp;
        SERVERPORT = serverPort;
        RUN_TIME = runTime;
        QUERY_SIZE = querySize;
        RESPONSE_SIZE = responseSize;
        DELAY_QUERY_RESPONSE = delayQueryResponse;
        MIN_PAYLOAD_SIZE = minPayloadSize;
        MAX_PAYLOAD_SIZE = maxPayloadSize;
        INTERVAL_TIME_MS = intervalTimeMs;
        BUFFER_SIZE = bufferSize;
        BURST_SIZE = burstSize;
        INTERVAL_BURST_TIME_MS = intervalBurstTimeMs;
    }

    public SiriClient(String serverIp, int serverPort, int runTime) {
    	this(serverIp, serverPort, runTime, 2500, 750, 0, 85, 500, 333, 9, 0, 0);
    }

    protected String getStringWithLengthAndFilledWithCharacter(int length, char charToFill) {
        if (length > 0) {
            char[] array = new char[length];
            Arrays.fill(array, charToFill);
            return new String(array);
        }
        return "";
    }

    /**
     * Return a random number in [@MIN_PAYLOAD_SIZE, @MAX_PAYLOAD_SIZE]
     * It manages 3 cases:
     *      1) remainToSend in [@MIN_PAYLOAD_SIZE, @MAX_PAYLOAD_SIZE]: return remainToSend
     *      2) remainToSend - @MAX_PAYLOAD_SIZE < MIN_PAYLOAD_SIZE: return random value in
     *          [@MIN_PAYLOAD_SIZE, @MAX_PAYLOAD_SIZE - @MIN_PAYLOAD_SIZE]
     *      3) else, return random value in [@MIN_PAYLOAD_SIZE, @MAX_PAYLOAD_SIZE]
     * @param remainToSend number of remaining bytes to send >= MIN_PAYLOAD_SIZE
     */
    private int sizeOfNextPacket(int remainToSend) {
        if (remainToSend < MIN_PAYLOAD_SIZE) throw new AssertionError();

        // Case 1)
        if (remainToSend <= MAX_PAYLOAD_SIZE && remainToSend >= MIN_PAYLOAD_SIZE) {
            return remainToSend;
        }

        int randomPart;

        // Case 2)
        if (remainToSend - MAX_PAYLOAD_SIZE < MIN_PAYLOAD_SIZE) {
            randomPart = random.nextInt(MAX_PAYLOAD_SIZE - 2 * MIN_PAYLOAD_SIZE + 1);
        }
        // Case 3)
        else {
            randomPart = random.nextInt(MAX_PAYLOAD_SIZE - MIN_PAYLOAD_SIZE + 1);
        }

        return MIN_PAYLOAD_SIZE + randomPart;
    }

    /**
     * Get a random value following a Poisson distribution of mean lambda
     * @param lambda mean of the Poisson distribution
     * @return random value following a Poisson distribution of mean lambda
     */
    public static int getPoisson(double lambda) {
        double L = Math.exp(-lambda);
        double p = 1.0;
        int k = 0;

        do {
            k++;
            p *= Math.random();
        } while (p > L);

        return k - 1;
    }

    /**
     * Sends the message entered by client to the server
     */
    public void sendMessage() {
        // if (out != null && !out.checkError() && osw != null) {
        if (socket != null && !socket.isClosed()) {
            int remainToBeSent = QUERY_SIZE;
            // If the server has a DB, use it, otherwise set to 0
            //int delaysToSend = delayTime.size();
            int delaysToSend = 0;
            StringBuffer sb = new StringBuffer();
//            for (int i = 0; i < delaysToSend; i++) {
//                sb.append(delayTime.get(0) + "&");
//                delayTime.remove(delayTime.get(0));
//            }
            sentTime[messageId] = System.currentTimeMillis();
            String startString = messageId + "&" + QUERY_SIZE + "&" + RESPONSE_SIZE + "&" +
                    DELAY_QUERY_RESPONSE + "&" + delaysToSend + "&" + sentTime[messageId] +
                    "&" + mac + "&" + sb.toString();
            messageId = (messageId + 1) % MAX_ID;
            int bytesToSend = Math.max(startString.length(), sizeOfNextPacket(remainToBeSent));
            // System.err.println("BytesToSend: " + bytesToSend);
            byte[] toSend;
            try {
                //osw.write(startString + getStringWithLengthAndFilledWithCharacter(bytesToSend - startString.length(), '0'));
                //osw.flush();
                toSend = (startString + getStringWithLengthAndFilledWithCharacter(bytesToSend - startString.length(), '0')).getBytes(StandardCharsets.US_ASCII);
                outputStream.write(toSend);
                outputStream.flush();
            } catch (IOException e) {
            	System.err.println("ERROR: OUTPUT STREAM ERROR");
            }
            // out.println(startString + getStringWithLengthAndFilledWithCharacter(bytesToSend - startString.length() - 1, '0'));
            // System.err.println("Sent " + startString + getStringWithLengthAndFilledWithCharacter(bytesToSend - startString.length() - 1, '0'));
            // out.flush();
            remainToBeSent -= bytesToSend;
            synchronized (this) {
                counter += bytesToSend;
            }

            try {
                while(remainToBeSent > 0) {
                    bytesToSend = sizeOfNextPacket(remainToBeSent);
                    //out.println(getStringWithLengthAndFilledWithCharacter(bytesToSend - 1, '0'));
                    //out.flush();

                        if (remainToBeSent == bytesToSend) {
                            //osw.write(getStringWithLengthAndFilledWithCharacter(bytesToSend - 1, '0') + "\n");
                            toSend = (getStringWithLengthAndFilledWithCharacter(bytesToSend - 1, '0') + "\n").getBytes(StandardCharsets.US_ASCII);
                        } else {
                            //osw.write(getStringWithLengthAndFilledWithCharacter(bytesToSend, '0'));
                            toSend = getStringWithLengthAndFilledWithCharacter(bytesToSend, '0').getBytes(StandardCharsets.US_ASCII);
                        }
                        //osw.flush();
                        outputStream.write(toSend);
                        outputStream.flush();

                    remainToBeSent -= bytesToSend;
                    synchronized (this) {
                        counter += bytesToSend;
                    }
                }
            } catch (IOException e) {
            	System.err.println("ERROR: OUTPUT STREAM ERROR");
                e.printStackTrace();
            }
        }
    }

    public void stopClient(){
        mRun = false;
        if (socket != null) {
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public static String getIPAddress(boolean useIPv4) {
        try {
            List<NetworkInterface> interfaces = Collections.list(NetworkInterface.getNetworkInterfaces());
            for (NetworkInterface intf : interfaces) {
                List<InetAddress> addrs = Collections.list(intf.getInetAddresses());
                for (InetAddress addr : addrs) {
                    if (!addr.isLoopbackAddress()) {
                        String sAddr = addr.getHostAddress();
                        //boolean isIPv4 = InetAddressUtils.isIPv4Address(sAddr);
                        boolean isIPv4 = sAddr.indexOf(':')<0;

                        if (useIPv4) {
                            if (isIPv4)
                                return sAddr;
                        } else {
                            if (!isIPv4) {
                                int delim = sAddr.indexOf('%'); // drop ip6 zone suffix
                                return delim<0 ? sAddr.toUpperCase() : sAddr.substring(0, delim).toUpperCase();
                            }
                        }
                    }
                }
            }
        } catch (Exception ex) { } // for now eat exceptions
        return "";
    }

    public void run(String macWifi) {

        mRun = true;
        mac = macWifi;

        try {
            //here you must put your computer's IP address.
            InetAddress serverAddr = InetAddress.getByName(SERVERIP);
            System.err.println("Me: " + getIPAddress(true));

            System.err.println("TCP Client: Connecting...");

            //create a socket to make the connection with the server
            socket = new Socket(serverAddr, SERVERPORT);
            // Needed to emulate any traffic
            socket.setTcpNoDelay(true);

            new Thread(new Runnable() {
                public void run() {
                	final long startTime = System.currentTimeMillis();
                    while (socket != null && !socket.isClosed()) {
                        try {
                            if (BURST_SIZE > 0 && pktCounter == BURST_SIZE) {
                              Thread.sleep(INTERVAL_BURST_TIME_MS);
                              pktCounter = 0;
                            } else {
                              Thread.sleep(INTERVAL_TIME_MS); //* getPoisson(3));
                            }
                            if ((System.currentTimeMillis() - startTime) >= RUN_TIME * 1000) {
                            	stopClient();
                            } else if (!socket.isClosed() && counter <= QUERY_SIZE * BUFFER_SIZE) {
                                sendMessage();
                                pktCounter++;
                            } else if (!socket.isClosed()) {
                                missed++;
                            }
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    }


                }
            }).start();


            try {

                //send the message to the server
                out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);
                outputStream = socket.getOutputStream();
                osw = new OutputStreamWriter(socket.getOutputStream());

                System.err.println("TCP Client: Done.");

                //receive the message which the server sends back
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                //in this while the client listens for the messages sent by the server
                while (mRun) {
                    serverMessage = in.readLine();
                    long receivedTime = System.currentTimeMillis();
                    // System.err.println("SERVER MESSAGE: " + ((serverMessage == null) ? "" : serverMessage));
                    if (serverMessage != null) {
                        int id = Integer.parseInt(serverMessage.split("&")[0]);
                        // System.err.println("ELAPSED TIME: " + (receivedTime - sentTime[id]));
                        delayTime.add(receivedTime - sentTime[id]);
                        synchronized (this) {
                            counter -= QUERY_SIZE;
                        }

                    }
                    serverMessage = null;

                }

                //System.err.println("RESPONSE FROM SERVER: Received Message: '" + serverMessage + "'");

            } catch (SocketException e) {
            	System.err.println("TCP: Socket closed");
            } catch (Exception e) {
            	System.err.println("TCP: Error " + e);

            } finally {
                //the socket must be closed. It is not possible to reconnect to this socket
                // after it is closed, which means a new socket instance has to be created.
                socket.close();
            }

        } catch (Exception e) {

        	System.err.println("TCP C: Error" + e);

        }

    }

    public static void usage() {
    	System.out.println("Usage: siriClient serverIP serverPort runTime [querySize responseSize delayQueryResponse "
    					   + "minPayloadSize maxPayloadSize intervalTimeMs bufferSize burstSize intervalBurstTimeMs]");
    }

    public static void main(String[] args) {
    	if (args.length != 3 && args.length != 12) {
    		usage();
    		System.exit(1);
    	}
    	String serverIp = args[0];
    	int serverPort = Integer.parseInt(args[1]);
    	int runTime = Integer.parseInt(args[2]);
    	SiriClient siriClient;

    	if (args.length == 12) {
    		int querySize = Integer.parseInt(args[3]);
    		int responseSize = Integer.parseInt(args[4]);
    		int delayQueryResponse = Integer.parseInt(args[5]);
    		int minPayloadSize = Integer.parseInt(args[6]);
    		int maxPayloadSize = Integer.parseInt(args[7]);
    		int intervalTimeMs = Integer.parseInt(args[8]);
    		int bufferSize = Integer.parseInt(args[9]);
        int burstSize = Integer.parseInt(args[10]);
        int intervalBurstTimeMs = Integer.parseInt(args[11]);
    		siriClient = new SiriClient(serverIp, serverPort, runTime, querySize, responseSize, delayQueryResponse,
    									minPayloadSize, maxPayloadSize, intervalTimeMs, bufferSize, burstSize, intervalBurstTimeMs);
    	} else {
    		siriClient = new SiriClient(serverIp, serverPort, runTime);
    	}

    	String mac = "00:00:00:00:00:00";
    	siriClient.run(mac);
    	System.out.println("missed: " + siriClient.missed);
    	for (long delay: siriClient.delayTime) {
    		System.out.println(delay);
    	}
	}
}
