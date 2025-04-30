
import React, { useState } from 'react';
import { cn } from "@/lib/utils";
import { Download, Maximize2, X } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent } from "@/components/ui/dialog";

interface ImagePreviewProps {
  imageUrl: string;
  alt?: string;
  className?: string;
  onRemove?: () => void;
  aspectRatio?: 'auto' | 'square' | 'video';
  allowFullScreen?: boolean;
  allowDownload?: boolean;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({
  imageUrl,
  alt = '이미지',
  className,
  onRemove,
  aspectRatio = 'auto',
  allowFullScreen = true,
  allowDownload = true,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `image-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getAspectRatioClass = () => {
    switch (aspectRatio) {
      case 'square':
        return 'aspect-square';
      case 'video':
        return 'aspect-video';
      default:
        return 'aspect-auto';
    }
  };

  return (
    <>
      <div className={cn('group relative rounded-lg overflow-hidden', className)}>
        <img 
          src={imageUrl} 
          alt={alt}
          className={cn(
            'w-full h-full object-cover',
            getAspectRatioClass()
          )}
        />
        
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="absolute top-2 right-2 flex gap-2">
            {allowFullScreen && (
              <Button
                variant="ghost"
                size="icon"
                className="bg-black/50 text-white hover:bg-black/70 h-8 w-8"
                onClick={() => setIsFullscreen(true)}
              >
                <Maximize2 size={16} />
              </Button>
            )}
            
            {allowDownload && (
              <Button
                variant="ghost"
                size="icon"
                className="bg-black/50 text-white hover:bg-black/70 h-8 w-8"
                onClick={handleDownload}
              >
                <Download size={16} />
              </Button>
            )}
            
            {onRemove && (
              <Button
                variant="ghost"
                size="icon"
                className="bg-black/50 text-white hover:bg-red-600 h-8 w-8"
                onClick={onRemove}
              >
                <X size={16} />
              </Button>
            )}
          </div>
        </div>
      </div>

      {allowFullScreen && (
        <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
          <DialogContent className="sm:max-w-[90vw] max-h-[90vh] p-0 bg-black border-none overflow-hidden">
            <div className="relative w-full h-full flex items-center justify-center">
              <img 
                src={imageUrl} 
                alt={alt}
                className="max-w-full max-h-[85vh] object-contain"
              />
              <Button
                variant="ghost"
                size="icon"
                className="absolute top-2 right-2 bg-black/50 text-white hover:bg-black/70 h-8 w-8"
                onClick={() => setIsFullscreen(false)}
              >
                <X size={16} />
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

export default ImagePreview;
