package upm.dit.giros;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.serialization.SerializationSchema;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessAllWindowFunction;
import org.apache.flink.streaming.api.windowing.windows.GlobalWindow;
import org.apache.flink.util.Collector;
import java.util.Collection;
import java.util.Iterator;
import java.util.LinkedHashMap;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONArray;

public class FlinkAggregation {
    
    public static void main(String[] args) throws Exception {

        // Initialization of the Flink streaming execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Kafka consumer subscribes to kafka broker: args[0] = kafka-service:9092 & input topics: args[1] = TD_rn
        KafkaSource<String> consumer = KafkaSource.<String>builder()
                .setTopics(args[1])
                .setGroupId("traffic-rate-group")
                .setBootstrapServers(args[0])
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer((DeserializationSchema<String>) new SimpleStringSchema())
                .build();

        // Kafka producer publishes in kafka broker: args[0] = kafka-service:9092 & output topics: args[2] = TP_rn
        KafkaSink<String> producer = KafkaSink.<String>builder()
                .setBootstrapServers(args[0])
                .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                        .setTopic(args[2])
                        .setValueSerializationSchema((SerializationSchema<String>) new SimpleStringSchema())
                        .build())
                .setDeliverGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();

        // Kafka data consuming source definiton
        DataStream<String> dss = env.fromSource(consumer, WatermarkStrategy.noWatermarks(), "Kafka Source");
        
        // Data source mapping for Kafka messages processing
        DataStream<String> metric_values = dss.map(new MapFunction<String, String>() {
            @Override
            public String map(String value) throws Exception {
                try {
                    System.out.println("\nMétricas extraídas de Kafka:" + value);

                } catch (JSONException e) {
                    e.printStackTrace();
                }
                System.out.println("\nValor de la métrica:" + value);
                return value;
            }
        });

        // Aggregation metrics event window
        metric_values.countWindowAll(2, 1).process(new EventsAggregation()).sinkTo(producer);

        // Initializes the Flink application execution
        env.execute("Kafka Source");
    }
        
        // Calculating aggregated events metrics function
        private static String aggregationMetrics(String metrics1, String metrics2) {
    
            // Empty JSON object result
            JSONObject result = new JSONObject(new LinkedHashMap<>());

            // Flag for ignoring events based on node failures (fault tolerance)
            Boolean ignore_event = false;
    
            try {
    
                // JSON object with original metrics extracted from Kafka in each event
                JSONObject rawMetrics1 = new JSONObject(metrics1);
                JSONObject rawMetrics2 = new JSONObject(metrics2);
    
                // Initial parameters of the input data
                String node_exporter = rawMetrics2.getString("node_exporter");
                //String router_type = rawMetrics2.getString("router_type");
                String epoch_timestamp = rawMetrics2.getString("epoch_timestamp"); 
                String experiment_id = rawMetrics2.getString("experiment_id");
                JSONArray interfaces = rawMetrics2.getJSONArray("interfaces");
                boolean flag_debug_params = rawMetrics2.getBoolean("flag_debug_params");
                JSONObject debug_params = rawMetrics2.getJSONObject("debug_params");
                boolean flag_original_metrics = debug_params.getBoolean("flag_original_metrics");
                int max_throughput = debug_params.getInt("max_throughput_mbps");
                int polling_interval = debug_params.getInt("polling_interval");
                int multiplier = debug_params.getInt("multiplier");
                //String collector_timestamp = debug_params.getString("collector_timestamp");
    
                // Events timestamp to calculate rate metrics
                Double timestamp1 = Double.parseDouble(rawMetrics1.getString("epoch_timestamp"));
                Double timestamp2 = Double.parseDouble(rawMetrics2.getString("epoch_timestamp"));
    
                // JSON array with original metrics from both events
                JSONArray metricArray1 = rawMetrics1.getJSONArray("metrics");
                JSONArray metricArray2 = rawMetrics2.getJSONArray("metrics");
    
                // Empty JSON array for aggregated metrics
                JSONArray mlMetrics = new JSONArray();
    
                // Interfaces label for output format
                JSONObject rateLabels = new JSONObject(new LinkedHashMap<>());
                rateLabels.put("name", "device");
                rateLabels.put("value", interfaces); 

                // Auxiliary variables for aggregated metrics calculus
                Double packetCounterTotal1 = 0.0;
                Double packetCounterTotal2 = 0.0;
                Double packetCounterRate = 0.0;
                Double packetRateValue = 0.0;
                Double byteRateValue = 0.0;
                Double byteCounterTotal1 = 0.0;
                Double byteCounterTotal2 = 0.0;
                Double byteCounterRate = 0.0;
                Double packetLength = 0.0;
                Double nodeOccupation = 0.0;
                
                // For each metrics in original metrics array
                for (int i = 0; i < metricArray2.length(); i++) {
    
                    // JSON object with original metrics
                    JSONObject metricObject1 = metricArray1.getJSONObject(i);
                    JSONObject metricObject2 = metricArray2.getJSONObject(i);
    
                    // JSON array with original metrics values
                    JSONArray metricValues1 = metricObject1.getJSONArray("values");
                    JSONArray metricValues2 = metricObject2.getJSONArray("values");
                    
                    // For each interface of original metrics
                    for (int j = 0; j < metricValues1.length(); j++) {
    
                        // JSON object with original metrics values per interface
                        JSONObject metricValue1 = metricValues1.getJSONObject(j);
                        JSONObject metricValue2 = metricValues2.getJSONObject(j);
    
                        // Original metrics values per interface
                        Double value1 = Double.parseDouble(metricValue1.getString("value"));
                        Double value2 = Double.parseDouble(metricValue2.getString("value"));    
    
                        // Aggregated metrics calculus for bytes and packets rates
                        Double time = (timestamp2 - timestamp1);
                        System.out.println("\nTime: " + time);
                        Double traffic_rate = (value2 - value1)/time;
                        
                        // Ignore events if node failure detected
                        ignore_event = ((time > (5 * polling_interval)) || (value1 > value2));
    
                        // Interface aggregated total and calculated rate metrics
                        switch (metricObject2.getString("name")) {
                            case "node_network_receive_packets_total":
                                packetCounterTotal1 += value1;
                                packetCounterTotal2 += value2;
                                packetCounterRate += traffic_rate;
                                break;
                            case "node_network_receive_bytes_total":
                                byteCounterTotal1 += value1;
                                byteCounterTotal2 += value2;
                                byteCounterRate += traffic_rate;
                                break;
                        }
                    }
                }

                // Interface aggregated packet rate metric scaled to 1:2000
                //packetRateValue = (packetCounterRate * multiplier);
                //System.out.println("\nMultiplier: " + multiplier);
                //System.out.println("\nPacket rate: " + packetRateValue);
                byteRateValue = ((byteCounterRate * 8) / 1000000);
                // Interface aggregated byte rate metric format
                JSONObject byteRateMetric = new JSONObject(new LinkedHashMap<>());
                byteRateMetric.put("name", "node_network_receive_bytes_total_rate");
                //packetRateMetric.put("description", "Calculated rate metric for " + "node_network_receive_packets_total");
                byteRateMetric.put("type", "rate");
                byteRateMetric.put("value", byteRateValue);
                mlMetrics.put(byteRateMetric);
                
                // Interface aggregated packet rate metric format
                JSONObject packetRateMetric = new JSONObject(new LinkedHashMap<>());
                packetRateMetric.put("name", "node_network_receive_packets_total_rate");
                //packetRateMetric.put("description", "Calculated rate metric for " + "node_network_receive_packets_total");
                packetRateMetric.put("type", "rate");
                packetRateMetric.put("value", packetCounterRate);
                mlMetrics.put(packetRateMetric);

                //Interface aggregated average packet length metric calculus
                if (packetCounterTotal2 > 0 && (packetCounterTotal2 - packetCounterTotal1) > 0) {
                    packetLength = (byteCounterTotal2 - byteCounterTotal1) / (packetCounterTotal2 - packetCounterTotal1);
                } else {
                    packetLength = 0.0;
                }

                // Interface aggregated node capacity occupation metric calculus
                nodeOccupation = ((byteCounterRate * 8) / ((double) max_throughput * 1000000));

                // Validate values to avoid non-finite numbers
                if (!Double.isFinite(byteRateValue)) byteRateValue = 0.0;
                if (!Double.isFinite(packetCounterRate)) packetCounterRate = 0.0;
                if (!Double.isFinite(packetLength)) packetLength = 0.0;
                if (!Double.isFinite(nodeOccupation)) nodeOccupation = 0.0;

                // Interface aggregated average packet length metric format     
                JSONObject packetLengthMetric = new JSONObject(new LinkedHashMap<>());
                packetLengthMetric.put("name", "node_network_average_received_packet_length");
                //packetLengthMetric.put("description", "Average length of received packets");
                packetLengthMetric.put("type", "length");
                packetLengthMetric.put("value", packetLength);
                mlMetrics.put(packetLengthMetric);

                // Interface aggregated node capacity occupation metric format
                JSONObject ocupationMetric = new JSONObject(new LinkedHashMap<>());
                ocupationMetric.put("name", "node_network_router_capacity_occupation");
                //ocupationMetric.put("description", "Router capacity occupation");
                ocupationMetric.put("type", "percentage");
                ocupationMetric.put("value", nodeOccupation);
                mlMetrics.put(ocupationMetric);
            
                // Aggregated metrics JSON format
                result.put("node_exporter", node_exporter);
                //result.put("router_type", router_type);
                result.put("experiment_id", experiment_id);
                result.put("epoch_timestamp", epoch_timestamp);
                result.put("interfaces", interfaces);
                result.put("flag_debug_params", flag_debug_params);
                debug_params.put("process_timestamp", String.valueOf(System.currentTimeMillis()).replaceFirst("(\\d+)(\\d{3})$", "$1.$2")
                );
                if (flag_debug_params) {
                    result.put("debug_params", debug_params);
                }
                if (flag_original_metrics) {
                result.put("metrics", metricArray2);
                }
                result.put("input_ml_metrics", mlMetrics);

            } catch (JSONException e) {
                e.printStackTrace();
            }

        System.out.println("\nFlink aggregated metrics: " + result.toString());
        return (!ignore_event ? result.toString() : null);
        
    }

    // Event window event aggregation
    public static class EventsAggregation extends ProcessAllWindowFunction<String, String, GlobalWindow> {

		private int size(Iterable data) {
			if (data instanceof Collection) {
				return ((Collection<?>) data).size();
			}
			int counter = 0;
			for (Object i : data) {
				counter++;
			}
			return counter;
		}

        // Process function for event aggregation using event window
		@Override
		public void process(Context context, Iterable<String> elements, Collector<String> out) throws Exception {
            // Window size = 2 events/window
			int windowSize = size(elements);
			if (windowSize == 2) {
                // Iterate over events in event window
				Iterator<String> it = elements.iterator();
                String new_metric = aggregationMetrics(it.next(), it.next());
                if (new_metric != null) {
                    out.collect(new_metric);
                }                
			}
		}
	}
}
