import torch
import torch.nn as nn

conv1_ksize = (15, 1)
conv2_ksize = (30, 1)
conv3_ksize = (32, 1)
conv4_ksize = (1, 1)
# conv5_ksize = (1, 1)

conv1_isize = 1
conv1_osize = 5
conv2_isize = conv1_osize
conv2_osize = 15
conv3_isize = conv2_osize
conv3_osize = 25
conv4_isize = conv3_osize
conv4_osize = 1
# conv5_isize = conv4_osize
# conv5_osize = 1

fc1_dropout_p = 0.3
fc2_dropout_p = 0.3

fc1_isize = 20
fc1_osize = 1


class ConvLayer(nn.Module):

    def __init__(self, isize, osize, ksize, maxpool=None):
        
        super(ConvLayer, self).__init__()

        self.layer = nn.Sequential(
            nn.Conv2d(isize, osize, ksize),
            nn.BatchNorm2d(osize),
            nn.ReLU()
        )

        # optional maxpool
        self.maxpool = None
        if maxpool:
            self.maxpool = nn.MaxPool2d(maxpool)

    def forward(self, x):
        x = self.layer(x)
        if self.maxpool:
            x = self.maxpool(x)
        return x


class LinearLayer(nn.Module):

    def __init__(self, isize, osize, dropout_p, norm=True, activate=True):

        super(LinearLayer, self).__init__()

        self.dropout = nn.Dropout(p=dropout_p)
        self.linear = nn.Linear(isize, osize)
        self.batch_norm = nn.BatchNorm1d(osize) if norm else None
        self.activate = nn.ReLU() if activate else None

    def forward(self, x):

        x = self.dropout(x)
        x = self.linear(x)
        if self.batch_norm:
            x = self.batch_norm(x)
        if self.activate:
            x = self.activate(x)
        return x

class ConvNet(nn.Module):

    def __init__(self):

        super(ConvNet, self).__init__()

        self.in_batch_norm = nn.BatchNorm2d(conv1_isize)
        self.feat_extractor = nn.Sequential(
            ConvLayer(conv1_isize, conv1_osize, conv1_ksize),
            ConvLayer(conv2_isize, conv2_osize, conv2_ksize),
            ConvLayer(conv3_isize, conv3_osize, conv3_ksize),
            ConvLayer(conv4_isize, conv4_osize, conv4_ksize),
        )
        self.fc_layer = nn.Sequential(
            LinearLayer(fc1_isize, fc1_osize, fc1_dropout_p, norm=False, activate=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        
        x = self.in_batch_norm(x)
        x = self.feat_extractor(x)

        # flatten the input
        batch_size = x.size()[0]
        x = x.view(batch_size, -1)

        # fc layer
        x = self.fc_layer(x)
        return x
