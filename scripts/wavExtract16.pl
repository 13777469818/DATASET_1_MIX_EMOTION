#!/usr/local/bin/perl

#以下脚本在 Sox 14.3.2 版本上测试通过

if ($#ARGV != 2) {
	print "Extract mono channel wave from stereo file\n";
	print "Usage: $0 sox_exe_file src_wave_path out_wave_path\n";
	exit(1);
}

$soxExeFile = $ARGV[0];
$inWavePath = $ARGV[1];
$outRawPath = $ARGV[2];

$inWavePath =~ s/\/$//;
$outRawPath =~ s/\/$//;

opendir(DIR, $inWavePath) || die "cannot open $inWavePath: $! \n";

print "Converting wave files to raw files ...\n";

while ($waveFile = readdir(DIR)) {

	if ($waveFile =~ /\.wav/i) {
		# Convert to lower case
		$waveFile =~ s/\.wav/\.wav/i;
		# Executing now
		# 把双声道文件采样成16000
		$cmd = "$soxExeFile $inWavePath/$waveFile $outRawPath/$waveFile.tmp.wav rate -s -a 16000 dither -s ";
		print "$cmd\n";
		system $cmd;
		# 分离双声道文件，去掉右声道
		$cmd = "$soxExeFile $outRawPath/$waveFile.tmp.wav $outRawPath/$waveFile remix 1";		
		system $cmd;
		$cmd = "rm $outRawPath/$waveFile.tmp.wav";
		system $cmd;
	}
}

closedir DIR;

print "Done!\n";
