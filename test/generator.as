import com.adobe.images.PNGEncoder;
import flash.filesystem.*;
import flash.display.*;

var _seed: uint = 0;

function random():Number
{
	_seed = (-2836 * int(_seed / 127773) + 16807 * (_seed % 127773)) & 0xFFFFFFFF;
	return _seed / 4294967296;
}

var frame: uint = 0;
var bmp:BitmapData;

while (true) {
	_seed = frame;
	
	var bmpWidth: uint = 100 + random() * 100;
	var bmpHeight: uint = 100 + random() * 100;
	var baseX: Number = random() * 400;
	var baseY: Number = random() * 400;
	var numOctaves: uint = random() * 32;
	var randomSeed: int;
	if (random() < 0.5)
		randomSeed = random() * -0x80000000 - 1;
	else
		randomSeed = random() * 0x80000000;
	
	var stitch: Boolean = random() >= 0.5;
	var fractalNoise: Boolean = random() >= 0.5;
	var channelOptions: uint = random() * 16;
	var grayScale: Boolean = random() >= 0.75;
	var offsets: Array = [];
	
	for (var i: int = 0; i < numOctaves; i++) {
		var offsetX: Number = random() * 200 - 100;
		var offsetY: Number = random() * 200 - 100;
		offsets.push(new Point(offsetX, offsetY));
	}
	
	if (bmp)
		bmp.dispose();
	
	bmp = new BitmapData(bmpWidth, bmpHeight);
	
	bmp.perlinNoise(
		baseX, // baseX
		baseY, // baseY
		numOctaves, // numOctaves
		randomSeed, // randomSeed
		stitch, // stitch
		fractalNoise, // fractalNoise
		channelOptions, // channelOptions
		grayScale, // grayScale
		offsets
	);
	
	var fileName: String = "generated/perlin-" + frame.toString() + ".png";
	
	trace(fileName);

	var res: ByteArray = PNGEncoder.encode(bmp);

	var file:File = File.applicationStorageDirectory.resolvePath(fileName);
	var stream:FileStream = new FileStream();
	stream.open(file, FileMode.WRITE);
	stream.writeBytes(res);
	stream.close();

	frame++;
};
