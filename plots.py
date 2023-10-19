import matplotlib.pyplot as plt

# Raw data:
# Cache size: 252818 * 1.1 + 1
#   FIFOTimed: hit rate 0.9208351029410581 (hits=5374897, misses=462084)
#   S3FIFONaiveTimed: hit rate 0.9407500212866892 (hits=5491140, misses=345841)
#   FIFOSized: hit rate 0.9355723446761263 (existing_hits=4599604, hits=861314, misses=376063)
#   S3FIFONaiveSized: hit rate 0.9284467432736204 (existing_hits=4599604, hits=819722, misses=417655)
# Cache size: 252818 * 1.2 + 1
#   FIFOTimed: hit rate 0.9340744813114862 (hits=5452175, misses=384806)
#   S3FIFONaiveTimed: hit rate 0.9531889858815713 (hits=5563746, misses=273235)
#   FIFOSized: hit rate 0.9490032604183567 (existing_hits=4599604, hits=939710, misses=297667)
#   S3FIFONaiveSized: hit rate 0.9423174411566527 (existing_hits=4599604, hits=900685, misses=336692)
# Cache size: 252818 * 1.3 + 1
#   FIFOTimed: hit rate 0.9438605333818972 (hits=5509296, misses=327685)
#   S3FIFONaiveTimed: hit rate 0.9619986770558273 (hits=5615168, misses=221813)
#   FIFOSized: hit rate 0.9583815674575606 (existing_hits=4599604, hits=994451, misses=242926)
#   S3FIFONaiveSized: hit rate 0.9522311277011181 (existing_hits=4599604, hits=958551, misses=278826)
# Cache size: 252818 * 1.4 + 1
#   FIFOTimed: hit rate 0.9514163229244708 (hits=5553399, misses=283582)
#   S3FIFONaiveTimed: hit rate 0.9683480210060647 (hits=5652229, misses=184752)
#   FIFOSized: hit rate 0.9652112967302788 (existing_hits=4599604, hits=1034316, misses=203061)
#   S3FIFONaiveSized: hit rate 0.9597531669196799 (existing_hits=4599604, hits=1002457, misses=234920)
# Cache size: 252818 * 1.5 + 1
#   FIFOTimed: hit rate 0.9574555750652606 (hits=5588650, misses=248331)
#   S3FIFONaiveTimed: hit rate 0.9731796283044265 (hits=5680431, misses=156550)
#   FIFOSized: hit rate 0.9703428878730289 (existing_hits=4599604, hits=1064269, misses=173108)
#   S3FIFONaiveSized: hit rate 0.9656192130829276 (existing_hits=4599604, hits=1036697, misses=200680)
# Cache size: 252818 * 1.6 + 1
#   FIFOTimed: hit rate 0.9623827797280821 (hits=5617410, misses=219571)
#   S3FIFONaiveTimed: hit rate 0.9770088338474975 (hits=5702782, misses=134199)
#   FIFOSized: hit rate 0.9743764798960285 (existing_hits=4599604, hits=1087813, misses=149564)
#   S3FIFONaiveSized: hit rate 0.970356936231247 (existing_hits=4599604, hits=1064351, misses=173026)
# Cache size: 252818 * 1.7 + 1
#   FIFOTimed: hit rate 0.9664062637860222 (hits=5640895, misses=196086)
#   S3FIFONaiveTimed: hit rate 0.9800295735072634 (hits=5720414, misses=116567)
#   FIFOSized: hit rate 0.9775699115690114 (existing_hits=4599604, hits=1106453, misses=130924)
#   S3FIFONaiveSized: hit rate 0.9742803685672439 (existing_hits=4599604, hits=1087252, misses=150125)
# Cache size: 252818 * 1.8 + 1
#   FIFOTimed: hit rate 0.9698460556921463 (hits=5660973, misses=176008)
#   S3FIFONaiveTimed: hit rate 0.9823951799740311 (hits=5734222, misses=102759)
#   FIFOSized: hit rate 0.9802084330923811 (existing_hits=4599604, hits=1121854, misses=115523)
#   S3FIFONaiveSized: hit rate 0.9775039528139633 (existing_hits=4599604, hits=1106068, misses=131309)
# Cache size: 252818 * 1.9 + 1
#   FIFOTimed: hit rate 0.9726879357667945 (hits=5677561, misses=159420)
#   S3FIFONaiveTimed: hit rate 0.9842654961528914 (hits=5745139, misses=91842)
#   FIFOSized: hit rate 0.9823215117541071 (existing_hits=4599604, hits=1134188, misses=103189)
#   S3FIFONaiveSized: hit rate 0.980183591483337 (existing_hits=4599604, hits=1121709, misses=115668)
# Cache size: 252818 * 2 + 1
#   FIFOTimed: hit rate 0.9750838661287402 (hits=5691546, misses=145435)
#   S3FIFONaiveTimed: hit rate 0.985779806375933 (hits=5753978, misses=83003)
#   FIFOSized: hit rate 0.9840814969245232 (existing_hits=4599604, hits=1144461, misses=92916)
#   S3FIFONaiveSized: hit rate 0.9823340182193501 (existing_hits=4599604, hits=1134261, misses=103116)

cache_sizes = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
hit_rates = {
    'fifo_timed': [0.920835, 0.934074, 0.943861, 0.951416, 0.957456, 0.962383, 0.966406, 0.969846, 0.972688, 0.975084],
    's3fifo_naive_timed': [0.940750, 0.953189, 0.961999, 0.968348, 0.973180, 0.977009, 0.980030, 0.982395, 0.984265, 0.985780],
    'fifo_sized': [0.935572, 0.949003, 0.958382, 0.965211, 0.970343, 0.974376, 0.977570, 0.980208, 0.982322, 0.984081],
    's3fifo_naive_sized': [0.928447, 0.942317, 0.952231, 0.959753, 0.965619, 0.970357, 0.974280, 0.977504, 0.980184, 0.982334],
}

# Raw data:
# 300M of invocation data
#   FIFOTimed: hit rate 0.9121682384511185 (hits=2656503, misses=255792)
#   S3FIFONaiveTimed: hit rate 0.9331661112627669 (hits=2717655, misses=194640)
#   FIFOSized: hit rate 0.9272113573659262 (existing_hits=2264190, hits=436123, misses=211982)
#   S3FIFONaiveSized: hit rate 0.9196839605877839 (existing_hits=2264190, hits=414201, misses=233904)
# 600M of invocation data
#   FIFOTimed: hit rate 0.9208351029410581 (hits=5374897, misses=462084)
#   S3FIFONaiveTimed: hit rate 0.9407500212866892 (hits=5491140, misses=345841)
#   FIFOSized: hit rate 0.9355723446761263 (existing_hits=4599604, hits=861314, misses=376063)
#   S3FIFONaiveSized: hit rate 0.9284467432736204 (existing_hits=4599604, hits=819722, misses=417655)
# 10G of invocation data
#   FIFOTimed: hit rate 0.9395890841838378 (hits=93865704, misses=6035099)
#   S3FIFONaiveTimed: hit rate 0.9585482511086523 (hits=95759740, misses=4141063)
#   FIFOSized: hit rate 0.9545653401804989 (existing_hits=76974768, hits=18387076, misses=4538959)
#   S3FIFONaiveSized: hit rate 0.9487840453094256 (existing_hits=76974768, hits=17809520, misses=5116515)
# Full invocation data (~1.2T)
#   FIFOTimed: hit rate 0.9518583536738067 (hits=11481138898, misses=580675608)
#   S3FIFONaiveTimed: hit rate 0.9689976008324465 (hits=11687869318, misses=373945188)
#   FIFOSized: hit rate 0.9659716855373767 (existing_hits=9093003074, hits=2558368215, misses=410443217)
#   S3FIFONaiveSized: hit rate 0.960785582735938 (existing_hits=9093003074, hits=2495814405, misses=472997027)

amount_of_data = [0, 1, 2, 3]
hit_rates_per_data = {
    'fifo_timed': [0.912168, 0.920835, 0.939589, 0.951858],
    's3fifo_naive_timed': [0.933166, 0.940750, 0.958548, 0.968998],
    'fifo_sized': [0.927211, 0.935572, 0.954565, 0.965972],
    's3fifo_naive_sized': [0.919684, 0.928447, 0.948784, 0.960786],
}

plt.figure(figsize=[12.8, 9.6])
for queue_type in hit_rates.keys():
    plt.plot(cache_sizes, hit_rates[queue_type], marker='o', label=queue_type)
plt.legend(loc='lower right')
plt.xlabel('Cache size multiplier')
plt.ylabel('Cache hit rate')
plt.minorticks_on()
plt.savefig('hit_rates_cache_size.jpg')
plt.show()

plt.figure(figsize=[12.8, 9.6], clear=True)

for queue_type in hit_rates_per_data.keys():
    plt.plot(amount_of_data, hit_rates_per_data[queue_type], marker='o', label=queue_type)
plt.legend(loc='lower right')
plt.xlabel('Amount of invocation data')
plt.ylabel('Cache hit rate')
plt.xticks([0, 1, 2, 3], ['300M', '600M', '10G', '1.2T'])

plt.savefig('hit_rates_invocation_data.jpg')
plt.show()