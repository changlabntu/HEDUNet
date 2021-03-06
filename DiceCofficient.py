import torch
import torch.nn as nn
import numpy as np

def accuracy(target, y_hat):
    seg_pred = torch.argmax(y_hat[:, 1:], dim=1)
    seg_acc = (seg_pred == target[:, 1]).float().mean()

    edge_pred = (y_hat[:, 0] > 0).float()
    edge_acc = (edge_pred == target[:, 0]).float().mean()

    return seg_acc , edge_acc

# dice cofficient for BCE
def BCEDiceCofficient(target , y_hat):
    smooth = 0.00001
    edge_target = target[:, 1]
    N = edge_target.size(0)
    edge_pred = (y_hat[:, 1:] > 0).float()
    edge_pred_flat = edge_pred.view(N, -1)
    edge_target_flat = edge_target.view(N, -1)

    seg_target = target[:, 0]
    n = seg_target.size(0)
    seg_pred = (y_hat[:, 0] > 0).float()
    seg_pred_flat = seg_pred.view(n, -1)
    seg_target_flat = seg_target.view(n, -1)

    edge_intersection = (edge_pred_flat * edge_target_flat).sum(1)
    edge_unionset = edge_pred_flat.sum(1) + edge_target_flat.sum(1)
    edge_acc = (2 * (edge_intersection + smooth) / (edge_unionset + smooth)).mean()

    seg_intersection = (seg_pred_flat * seg_target_flat).sum(1)
    seg_unionset = seg_pred_flat.sum(1) + seg_target_flat.sum(1)
    seg_acc = (2 * (seg_intersection + smooth) / (seg_unionset + smooth)).mean()

    return seg_acc, edge_acc


# dice cofficient for CE
if 0:
    def oldCEDiceCofficient(target , y_hat):
        n = int(y_hat.shape[1] / 2) # 2
    # for edge
        edge_target = target[:, 1]  # [8,256,224]
        edge_pred = y_hat[:, 2:]  # [8,2,256*224]
        edge_probs = edge_pred.reshape(edge_pred.shape[0] * edge_pred.shape[2] * edge_pred.shape[3],
                                       edge_pred.shape[1])  # (B * H * W, C)
        _, edge_pred = torch.max(edge_probs, 1)
        edge_target = edge_target.reshape(edge_target.shape[0] * edge_target.shape[1] * edge_target.shape[2])
        dice_edge = np.zeros(n)
        dice_tp_edge = np.zeros(n)
        dice_div_edge = np.zeros(n)
        for i in range(n):
            dice_tp_edge[i] += ((edge_pred == i) & (edge_target == i)).sum().item()
            dice_div_edge[i] += ((edge_pred == i).sum().item() + (edge_target == i).sum().item())
            dice_edge[i] = (2 * dice_tp_edge[i]) / dice_div_edge[i]
        #print("edge_pred: ", (edge_pred == 1).sum())
        #print("edge_target: ", (edge_target == 1).sum())
        #print("tp: ",  ((edge_pred == 1) & (edge_target == 1)).sum())
        edge_acc = torch.from_numpy(dice_edge[1:])

    # for seg
        seg_target = target[:, 0, ::]  # [8,256,224]
        seg_pred = y_hat[:, :2]  # [8,2,256*224]
        seg_probs = seg_pred.reshape(seg_pred.shape[0] * seg_pred.shape[2] * seg_pred.shape[3],
                                     seg_pred.shape[1])  # (B * H * W, C)
        _, seg_pred = torch.max(seg_probs, 1)
        seg_target = seg_target.reshape(seg_target.shape[0] * seg_target.shape[1] * seg_target.shape[2])

        dice_seg = np.zeros(n)
        dice_tp_seg = np.zeros(n)
        dice_div_seg = np.zeros(n)
        for i in range(n):
            dice_tp_seg[i] += ((seg_pred == i) & (seg_target == i)).sum().item()
            dice_div_seg[i] += ((seg_pred == i).sum().item() + (seg_target == i).sum().item())
            dice_seg[i] = (2 * dice_tp_seg[i]) / dice_div_seg[i]
        #print("seg_pred: ", (seg_pred == 1).sum())
        #print("seg_target: ", (seg_target == 1).sum())
        #print("tp seg: ",  ((seg_pred == 1) & (seg_target == 1)).sum())
        seg_acc = torch.from_numpy(dice_seg[1:])

        return seg_acc, edge_acc


def oldCEDiceCofficient(target, y_hat):
    # target (B, 2, H, W)
    # y_hat (B, 2*2, H, W)
    #n = int(y_hat.shape[1] / 2)

    seg_target = target[:, 0, ::]  # [8,256,224]
    #seg_target = seg_target.reshape(seg_target.shape[0] * seg_target.shape[1] * seg_target.shape[2])

    seg_pred = y_hat[:, :2, ::]  # [8,2,256*224]
    #seg_probs = seg_pred.reshape(seg_pred.shape[0] * seg_pred.shape[2] * seg_pred.shape[3],
    #                             seg_pred.shape[1])  # (B * H * W, C)
    seg_pred = torch.argmax(seg_pred, 1)

    q = ((seg_pred == 1) & (seg_target == 1)).sum().item()
    p = ((seg_pred == 1).sum().item() + (seg_target == 1).sum().item())
    dice = 2 * q / p
    #dice = 0.1
    dice = torch.from_numpy(np.array([dice]))

    return dice, 1 * dice, q, p


# dice cofficient for CE
def CEDiceCofficient(target, y_hat):
    smooth = 0.00001
    edge_target = target[:, 1]
    n = edge_target.size(0)
# for edge
    edge_target = target[:, 1]  # [8,256,224]
    edge_pred = (y_hat[:, 3] > 0).float()
    edge_pred = edge_pred.view(n ,-1)
    edge_target = edge_target.view(n, -1)

    dice_tp_edge = (edge_pred * edge_target).sum(1)
    dice_div_edge = edge_pred.sum(1) + edge_target.sum(1)

    edge_acc = (2 * (dice_tp_edge +smooth) / (dice_div_edge + smooth)).mean()
# for seg
    seg_target = target[:, 0, ::]  # [8,256,224]
    seg_pred = (y_hat[:, 1] > 0).float()
    seg_pred = seg_pred.view(n, -1)
    seg_target = seg_target.view(n, -1)
    dice_tp_seg = (seg_pred * seg_target).sum(1)
    dice_div_seg = seg_pred.sum(1) + seg_target.sum(1)
    seg_acc = (2 * (dice_tp_seg + smooth) / (dice_div_seg +smooth)).mean()

    return seg_acc, edge_acc



