#!/usr/bin/perl

# ------------------------------------ bmp.pm ---------------------------------------
# Copyright (c) 2004 - Sckriptke - Enrique F. Castañón
# Licensed under the GNU GPL.
# bmp.pm Version *** BETA ***
# 4 abril 2004
# -----------------------------------------------------------------------------------
# http://Skriptke.LoCuaL.com/
# -----------------------------------------------------------------------------------
#
# Maneja archivos con formato BMP 
# ** SOLO ** archivos de 8 bit de color
# 
# 

package bmp;

sub new {
  my $class = shift;
  my ($file) = @_;
  $self = bless {}, $class;
  
  $self->{'file'} = $file;

  %{$self->{'BITMAPHEADER'}} = (
      # BitMapFileHeader
      '00_bfType'          =>0, # (2 byte) Tipo de archivo, contiene 'BM' siempre
      '01_bfSize'          =>0, # (4 byte) Tamaño del archivo en bytes.
      '02_bfReserved1'     =>0, # (2 byte) Reservado. Contiene ceros simpre.
      '03_bfReserved2'     =>0, # (2 byte) Reservado. Contiene ceros simpre.
      '04_bfOffbits'       =>0, # (4 byte) Distancia en bytes entre BITMAPINFOHEADER y el mapa de bits. Si contiene cero RGBQUAD no esta presente.
      # BitMapInfoHeader
      '05_biSize'          =>0, # (4 byte) Numero de bytes que ocupa BITMAPHEADER.
      '06_biWidth'         =>0, # (4 byte) Anchura del bitmap
      '07_biHeight'        =>0, # (4 byte) Altura del bitmap
      '08_biPlanes'        =>0, # (2 byte) Numero de planos de color (siempre 1)
      '09_biBitCount'      =>0, # (2 byte) Bits por pixel (1,4,8,24)
      '10_biCompression'   =>0, # (4 byte) Compresion utilizada (=0 Sin compresión), (=1 RLE4), (=2 RLE8).
      '11_biSizeImage'     =>0, # (4 byte) Tamaño en bytes de la imagen
      '12_biXpelsPerMeter' =>0, # (4 byte) Resolución horizontal
      '13_biYpelsPerMeter' =>0, # (4 byte) Resolución vertical
      '14_biClrUsed'       =>0, # (4 byte) Numero de indides de color utilizados. Si biBitCount=24 no importa
      '15_biClrImportant'  =>0, # (4 byte) Colores importantes (=0 todos)
  );
  
  %{$self->{'size'}{'BITMAPHEADER'}} = (
          '00_bfType'          => 2,
          '01_bfSize'          => 4,
          '02_bfReserved1'     => 2,
          '03_bfReserved2'     => 2,
          '04_bfOffbits'       => 4,
          '05_biSize'          => 4, 
          '06_biWidth'         => 4,
          '07_biHeight'        => 4,
          '08_biPlanes'        => 2,
          '09_biBitCount'      => 2,
          '10_biCompression'   => 4,
          '11_biSizeImage'     => 4, 
          '12_biXpelsPerMeter' => 4,
          '13_biYpelsPerMeter' => 4,
          '14_biClrUsed'       => 4,
          '15_biClrImportant'  => 4,
  );
  
  %{$self->{'type'}{'BITMAPHEADER'}} = (
          '00_bfType'          => "a2",
          '01_bfSize'          => "L",
          '02_bfReserved1'     => "C2",
          '03_bfReserved2'     => "C2",
          '04_bfOffbits'       => "L",
          '05_biSize'          => "L", 
          '06_biWidth'         => "L",
          '07_biHeight'        => "L",
          '08_biPlanes'        => "C2",
          '09_biBitCount'      => "C2",
          '10_biCompression'   => "L",
          '11_biSizeImage'     => "L",  
          '12_biXpelsPerMeter' => "C4",
          '13_biYpelsPerMeter' => "C4",
          '14_biClrUsed'       => "C4",
          '15_biClrImportant'  => "C4",
  );
  
  # RGBQUAD
  $self->{'RGBQUAD'}{'1_rgbBLUE'}     = [];
  $self->{'RGBQUAD'}{'2_rgbGREEN'}    = [];
  $self->{'RGBQUAD'}{'3_rgbRED'}      = [];
  $self->{'RGBQUAD'}{'4_rgbReserved'} = [];
  
  # bitmap
  $self->{'line'} = [];
  
  $self->get($self->{'file'}) if $self->{'file'};

  return $self;
}

sub print_header {
  my $self = shift;

  foreach my $key (sort keys %{$self->{'BITMAPHEADER'}}) {
    print $key,':',$self->{'BITMAPHEADER'}{$key},"\n";
  }

}  

# devuelve la image para salida
sub out {
  my $self = shift;
  my $out;

  # formatea la cabecera de la imagen
  foreach my $key (sort keys %{$self->{'size'}{'BITMAPHEADER'}}) {
    my $format = $self->{'type'}{'BITMAPHEADER'}{$key};
    $out .= pack($format, $self->{'BITMAPHEADER'}{$key});
  }
  
  # la paleta
  my $count = 0;
  foreach ( @{$self->{'RGBQUAD'}{'1_rgbBLUE'}} ) {
    foreach (sort keys %{$self->{'RGBQUAD'}}) {
      $out .= pack("C", $self->{'RGBQUAD'}{$_}[$count]);
    }
    $count++;
  }
  
  # el mapa de bit
  foreach (@{$self->{'line'}}) {
    $out .= $_;
    for ($self->{'BITMAPHEADER'}{'06_biWidth'}+1..$self->length_line) {
      $out .= pack("C",0x00);
    }
      
  }
  
  return $out;
}

# añade la imagen a la derecha (transforma esta imagen aumentando en ancho)
sub addr {
  my $self = shift;
  my ($bmp) = @_; 
  
  my $count = 0;
  foreach ( @{$bmp->{'line'}} ) {
    $self->{'line'}[$count] .= $bmp->{'line'}[$count];
    $count++;
  }
  
  foreach ( @{$bmp->{'RGBQUAD'}{'1_rgbBLUE'}} ) {
    foreach (sort keys %{$bmp->{'RGBQUAD'}}) {
      $self->{'RGBQUAD'}{$_} = $bmp->{'RGBQUAD'}{$_};
    }
  }
  
  $self->{'BITMAPHEADER'}{'00_bfType'}          = 'BM';      
  $self->{'BITMAPHEADER'}{'02_bfReserved1'}     = 0;
  $self->{'BITMAPHEADER'}{'03_bfReserved2'}     = 0;
  $self->{'BITMAPHEADER'}{'04_bfOffbits'}       = $bmp->{'BITMAPHEADER'}{'04_bfOffbits'};
  $self->{'BITMAPHEADER'}{'05_biSize'}          = $bmp->{'BITMAPHEADER'}{'05_biSize'};
  $self->{'BITMAPHEADER'}{'06_biWidth'}        += $bmp->{'BITMAPHEADER'}{'06_biWidth'};
  $self->{'BITMAPHEADER'}{'07_biHeight'}        = $bmp->{'BITMAPHEADER'}{'07_biHeight'};
  # data_size utiliza 05_biSize 06_biWidth si se llama sin parametros
  # por esa razon BITMAPHEADER se define en este orden
  $self->{'BITMAPHEADER'}{'01_bfSize'}          = $self->data_size();
  $self->{'BITMAPHEADER'}{'08_biPlanes'}        = 1;
  $self->{'BITMAPHEADER'}{'09_biBitCount'}      = $bmp->{'BITMAPHEADER'}{'09_biBitCount'};
  $self->{'BITMAPHEADER'}{'10_biCompression'}   = $bmp->{'BITMAPHEADER'}{'10_biCompression'};
  $self->{'BITMAPHEADER'}{'11_biSizeImage'}    += $bmp->{'BITMAPHEADER'}{'11_biSizeImage'}; 
  $self->{'BITMAPHEADER'}{'12_biXpelsPerMeter'} = $bmp->{'BITMAPHEADER'}{'12_biXpelsPerMeter'};
  $self->{'BITMAPHEADER'}{'13_biYpelsPerMeter'} = $bmp->{'BITMAPHEADER'}{'13_biYpelsPerMeter'};
  $self->{'BITMAPHEADER'}{'14_biClrUsed'}       = $bmp->{'BITMAPHEADER'}{'14_biClrUsed'};
  $self->{'BITMAPHEADER'}{'15_biClrImportant'}  = $bmp->{'BITMAPHEADER'}{'15_biClrImportant'};

  return;
}

sub get {
  my $self = shift;
  my ($file) = @_;

  open (IMAGE, "$file") || print "error $file";
  binmode IMAGE;
  
  # lee la cabecera de la imagen
  my $count;
  foreach my $key (sort keys %{$self->{'size'}{'BITMAPHEADER'}}) {
    my $value;
    for ( 1..$self->{'size'}{'BITMAPHEADER'}{$key} ) {
      $value .= getc(IMAGE);
      $count++;
    }
    my $format = $self->{'type'}{'BITMAPHEADER'}{$key};
    $self->{'BITMAPHEADER'}{$key} = unpack($format, $value);
  }
  
  # lee el resto de la cabecera si existe
  for ( $count..$self->{'BITMAPHEADER'}{'05_biSize'} ) {
    getc(IMAGE);
  }

  # lee la paleta
  # si bfOffbits contiene cero RGBQUAD no esta presente.
  my $n=0;
  while ( $count < $self->{'BITMAPHEADER'}{'04_bfOffbits'} ) {
    foreach (sort keys %{$self->{'RGBQUAD'}}) {
      $self->{'RGBQUAD'}{$_}[$n] = unpack("C",getc(IMAGE));
      $count++;
    }
    $n++;
  }


  # lee el mapa de bit
  if ( $self->{'BITMAPHEADER'}{'09_biBitCount'} <= 4 ) {
    # no soportado de momento
  } elsif ( $self->{'BITMAPHEADER'}{'09_biBitCount'} == 8 ) {
    for (1..$self->{'BITMAPHEADER'}{'07_biHeight'}) { 
      my $line;
      for (1..$self->length_line) {
        if ( $_ > $self->{'BITMAPHEADER'}{'06_biWidth'} ) {
          getc(IMAGE);
          $count++;
          next;
        }
        $line .= getc(IMAGE);
        $count++;
      }
      push (@{$self->{'line'}}, $line);
      #print $line,"\n";
    }
  } elsif ( $self->{'BITMAPHEADER'}{'09_biBitCount'} == 16 ) {
    # no soportado de momento
  } elsif ( $self->{'BITMAPHEADER'}{'09_biBitCount'} == 24 ) {
    # no soportado de momento
  } elsif ( $self->{'BITMAPHEADER'}{'09_biBitCount'} == 32 ) {
    # no soportado de momento
  } else {
    # error en el formato de archivo.
  }
  
  close IMAGE;
 
  return; 
}

sub noise {
  my $self = shift;
  my ($p) = @_; 
  
  my $biClrUsed = $self->{'BITMAPHEADER'}{'14_biClrUsed'};
  $biClrUsed = 256 if ! $biClrUsed;
  my $m = $biClrUsed * $p / 100;
  
  foreach (@{$self->{'line'}}) {
    my $line;
    foreach my $c (split(//,$_)) {
      $c = unpack("C",$c);
      my $r = int rand $m;
      if ( $r+$c >= $biClrUsed ) {
        if ( $c-$r < 0 ) {
          $c -= int rand $c;
        } else {
          $c -= $r;
        }
      } else {
        $c += $r;
      }
      $c = pack("C",$c);
      $line .= $c;
    }
    $_ = $line;
  }
}

# las lineas del mapa de bit son palabras de 32, multiplos de 4
sub length_line {
  my $self = shift;
  my ($biWidth) = @_; 
  
  if (!$biWidth) {
    $biWidth = $self->{'BITMAPHEADER'}{'06_biWidth'};
  }
  
  my $pad = 4 - ($biWidth % 4);
  $pad = 0 if $pad == 4;
 
  return $biWidth + $pad;
}

sub data_size {
  my $class = shift;
  my($biWidth, $biHeight, $bfOffbits) = @_;
  
  if (!$biWidth) {
    $biWidth   = $self->{'BITMAPHEADER'}{'06_biWidth'};
    $biHeight  = $self->{'BITMAPHEADER'}{'07_biHeight'};
    $bfOffbits = $self->{'BITMAPHEADER'}{'04_bfOffbits'};
  }
  
  return $bfOffbits + ($self->length_line($biWidth) * $biHeight);
}

1; 
  


