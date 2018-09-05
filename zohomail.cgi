#!/usr/local/cpanel/3rdparty/bin/perl

BEGIN {
    unshift @INC, '/usr/local/cpanel';
    unshift @INC, '/usr/local/cpanel/scripts';
    unshift @INC, '/usr/local/cpanel/bin';
    unshift @INC, '/usr/local/share/perl5';
}
use strict;
use warnings;
use JSON;
use CGI qw(:standard);
use Whostmgr::HTMLInterface();
Whostmgr::HTMLInterface::defheader('Zoho Mail','','',0,1,0,'');
Whostmgr::HTMLInterface::starthtml();
use Whostmgr::NVData;
use LWP::UserAgent;
use Data::Dumper;
use MIME::Base64;
my $state = 12;
use POSIX qw( strftime );


#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#Accepting the data submitted in the form and redirecting to allow permission

my $q = new CGI;
if ($q->param('zmr_ci') != "") {
  Whostmgr::NVData::set("reseller_details",$q->param('zmr_dr')."__".$q->param('zmr_ci')."__".$q->param('zmr_cs')."__".$q->param('zmr_ru'));

  my $url = 'https://accounts.zoho'.$q->param('zmr_dr').'/oauth/v2/auth?response_type=code&client_id='.$q->param('zmr_ci').
            '&scope=VirtualOffice.partner.organization.CREATE,VirtualOffice.partner.organization.READ,VirtualOffice.organization.READ,VirtualOffice.organization.domains.UPDATE&redirect_uri='.$q->param('zmr_ru').'&prompt=consent&access_type=offline&state='.$state;
    print '
    <head> <meta http-equiv="refresh" content="0; url='.$url.'"/>
    </head>
      ';
}
if ($q->param('zoid') != "") {
  my @resellerdetails = split(/__/, Whostmgr::NVData::get("reseller_details"));
  domainverification($resellerdetails[0],$q->param('zoid'),decode_base64($resellerdetails[5]),$q->param('domainName'));
}

if ($q->param('gt_det') != "") {
  my @resellerdetails = split(/__/, Whostmgr::NVData::get("reseller_details"));
  getchilddomaindetails($resellerdetails[0],$q->param('gt_det'),decode_base64($resellerdetails[5]),$q->param('gt_dn'));
}
if ($q->param() == "" && Whostmgr::NVData::get('authorization_status') eq "Success") {
  print '<head><link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
  <body><div class="zmMsg zmSucMsg">
  <i class="tickIco">
  </i>
  <span>Authentication is successful</span>
  </div></body>
  ';
} 
if (Whostmgr::NVData::get('authorization_status') eq "Failed") 
{
  print '<head><link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
  <body><div class="zmMsg zmErrMsg">
  <i class="tickIco">
  </i>
  <span>Authentication failure</span>
  </div></body>
  ';

}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#Utilizing the code to generate the refresh token and persist it for future requests!


if (length $ENV{'QUERY_STRING'}) {
  my @resellervalues = split(/&/, $ENV{'QUERY_STRING'});
  if ($resellervalues[0] eq 'action=verify') {
    
    } 
  else {
  my @resellerdetails = split(/__/, Whostmgr::NVData::get("reseller_details"));
  my $urlToRefTok = 'https://accounts.zoho'.$resellerdetails[0]
  .'/oauth/v2/token?'.$resellervalues[1].'&grant_type=authorization_code&client_id='.$resellerdetails[1]
  .'&client_secret='.$resellerdetails[2].'&redirect_uri='.$resellerdetails[3]
  .'&scope=VirtualOffice.partner.organization.CREATE,VirtualOffice.partner.organization.READ,VirtualOffice.organization.READ,VirtualOffice.organization.domains.UPDATE&state='.$state;
    my $ua = new LWP::UserAgent;
    my $req = new HTTP::Request POST => $urlToRefTok;
    my $res = $ua->request($req);
    if ($res->is_success) {
          my $decodedresponse = decode_json($res->content);
          print '<br><br>';
          if (length $decodedresponse->{'refresh_token'}) {
            Whostmgr::NVData::set("ZM_TIMESTAMP",time());
            Whostmgr::NVData::set("reseller_details",
                        $resellerdetails[0]."__".$resellerdetails[1]."__".$resellerdetails[2]
                        ."__".$resellerdetails[3]."__".encode_base64($decodedresponse->{'refresh_token'})."__".
                        encode_base64($decodedresponse->{'access_token'}));
            Whostmgr::NVData::set("authorization_status","Success");
          } else {
            Whostmgr::NVData::set("authorization_status","FAILED:  ".$decodedresponse->{'error'}.
              "Sorry for the inconvenience. Send this screenshot to support[at]zohomail[dot]com for further assistance.");
          }
      }
    else {
        Whostmgr::NVData::set("authorization_status","Failed");
          print $res->status_line, "\n";
      }
      print '
    <head> <meta http-equiv="refresh" content="0; url='.$resellerdetails[3].'"/>
    </head>
      ';
    }
}
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#Design to display the webmail UI and link to mail control panel. Also a provision to re-authenticate. A provision to check the domain verification status! Fetching all his 
#child Organization details.

if (Whostmgr::NVData::get('authorization_status') eq "Success") {
  my @resellerdetails = split(/__/, Whostmgr::NVData::get("reseller_details"));
  my @resellerorgvalues;
  my $lengthOrgs;
  my $access_token;
  if (time()- Whostmgr::NVData::get("ZM_TIMESTAMP") > 3000) {
        my $fetchaccesstokenurl = "https://accounts.zoho".$resellerdetails[0]."/oauth/v2/token?refresh_token=".decode_base64($resellerdetails[4])
                                 ."&grant_type=refresh_token&client_id=".$resellerdetails[1]
                                 ."&client_secret=".$resellerdetails[2]
                                 ."&redirect_url=".$resellerdetails[3]
                                 ."&scope=VirtualOffice.partner.organization.CREATE,VirtualOffice.partner.organization.READ,VirtualOffice.organization.READ,VirtualOffice.organization.domains.UPDATE";
        my $ua = new LWP::UserAgent;
        my $req = new HTTP::Request POST => $fetchaccesstokenurl;
        my $res = $ua->request($req);
        if ($res->is_success) {
        my $decodedresponse = decode_json($res->content);
        if (length $decodedresponse->{'access_token'}) {
            Whostmgr::NVData::set("reseller_details",$resellerdetails[0]."__".$resellerdetails[1]
                                        ."__".$resellerdetails[2]."__".$resellerdetails[3]
                                        ."__".$resellerdetails[4]."__".encode_base64($decodedresponse->{'access_token'}));
            Whostmgr::NVData::set("ZM_TIMESTAMP",time());
            $access_token=$decodedresponse->{'access_token'};
            } else {
              print "This action could not be performed. Please contact support[at]zohomail[dot]com for more details.";
            }
          } 
          }
    else {
        $access_token = decode_base64($resellerdetails[5]);
    }
    my $getallchildorgsurl = 'https://mail.zoho'.$resellerdetails[0].'/api/organization?mode=getCustomerOrgDetails';
    my $encUrl = 'https://mailadmin.zoho'.$resellerdetails[0].'/cpanel/index.do#managecustomers';
    my $uaco = new LWP::UserAgent;
    my $reqco = new HTTP::Request GET => $getallchildorgsurl;
    $reqco->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
    my $resco = $uaco->request($reqco);
    if ($resco->is_success) {
        my $decodechildorgs = decode_json($resco->content);
        my $zoid_domain = '';
        for my $item( @{$decodechildorgs->{'data'}} ){
               if(length($item->{'domainName'}) > 0)
               {
                       $zoid_domain = $item->{'zoid'}.'__'.$item->{'domainName'}.'__'.$item->{'superAdmin'}.'__'.$item->{'isVerified'}.'__'.$zoid_domain;
                     }
            }
        @resellerorgvalues = split(/__/,$zoid_domain);
        $lengthOrgs = @resellerorgvalues;
      } else 
      {
        print $resco->status_line;
      }
    print '
    <div class="zm_page zm_thmBasic">
    <div class="zm_page_header">
                <h1><img src="assets/images/zoho.png" /><span>Zoho Mail - Manage Customers</span>
                </h1><div style="margin-top:8px;"> 
                <a href="'.$encUrl.'" target=_blank>Manage Customers</a> |
                <a href="https://mail.zoho'.$resellerdetails[0].'" target=_blank>Webmail</a>
                </div>
                
            </div>

    </div>
    <table>
    <tr>
    <th>Domain Name</th>
    <th> Super Admin</th>
    <th>Verification Status</th>
    <th>More Details</th>
    </tr>';
  for ( $a = 0; $a < $lengthOrgs; $a = $a + 4) {
    my $detailFlag = '0';
    my $domainVerificationFlag = '0';
    my $boldFlag = '0';
    if ($q->param('gt_det') != "") {
      $detailFlag = '1';
    } 
    if ($q->param('zoid') != "") {
      $domainVerificationFlag = '1';
    }
    if (($detailFlag eq '1' || $domainVerificationFlag eq '1') && ($q->param('zoid') eq $resellerorgvalues[$a] || $q->param('gt_det') eq $resellerorgvalues[$a])) {
      $boldFlag = '1';
    }
    my $verificationStatus;
    if ($resellerorgvalues[$a+3] eq 0) {
      $verificationStatus = '<form method=post action=zohomail.cgi>
      <input type="hidden" value='.$resellerorgvalues[$a].' name="zoid"/>
      <input type="hidden" value='.$resellerorgvalues[$a+1].' name="domainName"/>
      <center><button class="btntable"> Verify </button></center>
      </form>';
    } else {
      $verificationStatus = 'Verified';
    }
    if ($boldFlag eq '1') {
       print '<tr class="zm_selected">
            <td><b>'.$resellerorgvalues[$a+1].'</b></td>
             <td><b>'.$resellerorgvalues[$a+2].'</b></td>
             <td><b>'.$verificationStatus.'</b></td>
             <td><form method=post action=zohomail.cgi>
             <input type="hidden" value='.$resellerorgvalues[$a].' name="gt_det"/>
             <input type="hidden" value='.$resellerorgvalues[$a+1].' name="gt_dn"/>
             <center><button class="btntable"> Get details </button></center>
             </form>
             </td>
            </tr>';
            } else {
              print '<tr>
                     <td>'.$resellerorgvalues[$a+1].'</td>
                     <td>'.$resellerorgvalues[$a+2].'</td>
                     <td>'.$verificationStatus.'</td>
                     <td><form method=post action=zohomail.cgi>
                     <input type="hidden" value='.$resellerorgvalues[$a].' name="gt_det"/>
                     <input type="hidden" value='.$resellerorgvalues[$a+1].' name="gt_dn"/>
                     <center><button class="btntable"> Get details </button></center>
                     </form>
                     </td>
                     </tr>';

            }
  }
  print '</table><br>';
} 

else {
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#Designing the form to input the parameters from the reseller Showing it if the authentication status is failure.


print '
 <head>
    <meta charset="UTF-8">
    <title>Zoho Mail</title>
    <link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
<body>
    <div class="zm_page zm_thmBasic">
        <div class="zm_page_content">
            <div class="zm_page_header">
                <h1><img src="assets/images/zoho.png" /><span>Zoho Mail</span></h1>
            </div>
            <div class="zm_pageInner">
            <form method="post" action="zohomail.cgi" class="zm_form">
                <div class="zm_form_row">
                    <label class="zm_form-label">Domain</label>
                    <select name="zmr_dr" class="zm_form-input zm_form-input-select">
                        <option name=".com" default>.com</option>
                        <option name=".eu" >.eu</option>
                    </select> <i class="zm_form_row-info">The name of the region the account is configured</i> </div>
                <div class="zm_form_row">
                    <label class="zm_form-label">Client ID</label>
                    <input name="zmr_ci" type="text" class="zm_form-input" /> <i class="zm_form_row-info">Created in the <a href="https://accounts.zoho.com/developerconsole"> developer console </a></i> </div>
                <div class="zm_form_row">
                    <label class="zm_form-label">Client Secret</label>
                    <input name="zmr_cs" type="text" class="zm_form-input" /> <i class="zm_form_row-info">Created in the <a href="https://accounts.zoho.com/developerconsole"> developer console </a></i> </div>
                <div class="zm_form_row">
                    <label class="zm_form-label">Authorization Redirect URL</label>
                    <input name="zmr_ru" type="text" class="zm_form-input" readonly value="https://'.$ENV{'HOST'}.':'.$ENV{'SERVER_PORT'}.$ENV{'SCRIPT_URI'}.'" /> <i class="zm_form_row-info">Copy this URL into your developer console</i> <br></div>
                
                <div class="zm_form_row form_row-btn"><button class="zm_btn" name="zm_auth">Authenticate</button> </div>
            </form>
        </div>
      </div>
    </div>
</body>'
;
}

#-----------------------------------------------------------------------------------------------------
# A sub routine to perform the domain verification in Zoho mail side after the CName is configured.
sub domainverification {
   my ($region, $zoid, $access_token, $domainName) = @_;
   my $result = 'null';
   my %json_string = ('domainName' => $domainName, 'mode' => 'verifyDomainByCName');
   my $json_body = encode_json \%json_string;   #Constructing the json body for verifying the child organization
   my $childomainurl = 'https://mail.zoho'.$region.'/api/organization/'.$zoid.'/domains/'.$domainName;
   my $ua = new LWP::UserAgent;
   my $req = new HTTP::Request PUT => $childomainurl;
   $req->header('Content-Type' => 'application/json');
   $req->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
   $req->content($json_body);
   my $res = $ua->request($req);
   my $decodverifystatus = decode_json($res->content);
   if ($res->code() eq 400) {
    print '<head><link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
       <body>
       <div class="zmcMsg zmcErrMsg">
       <i class="zm_tickIco"></i>
       <span>'.$decodverifystatus->{'data'}->{'moreInfo'}.'
       </span>
       </div>
      ';
   }
   if ($res->code() eq 200) {

    print '
    <div class="zmcMsg zmConSucMsg">
             <i class="zm_tickIco"></i>
             <span style="color:black; font-size:16px;">
              Domain Verification Success
              </span>
              </div>
              ';
   } 
   return $result;
}


#-----------------------------------------------------------------------------------------------------
# A sub routine to perform the additional information of Child Organization.
sub getchilddomaindetails {
  my ($region, $zoid, $access_token, $domainName) = @_;
  my $result = 'null';
  my $childOrgurl = 'https://mail.zoho'.$region.'/api/organization/'.$zoid;
  my $childomainurl = 'https://mail.zoho'.$region.'/api/organization/'.$zoid.'/domains/'.$domainName;
  my $encryptedZoidURL = 'https://mail.zoho'.$region.'/api/organization/'.$zoid.'?fields=encryptedZoid';
  my $encUrl = 'https://mailadmin.zoho.com/cpanel/index.do#managecustomers';
  my $ua = new LWP::UserAgent;
  my $reqEz = new HTTP::Request GET => $encryptedZoidURL;
  $reqEz->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
  my $resEz = $ua->request($reqEz);
  if ($resEz->code() eq 200) {
    my $decEnZoid = decode_json($resEz->content);
    $encUrl = 'https://mail.zoho'.$region.'/cpanel/index.do?zoid='.$decEnZoid->{'data'}->{'encryptedZoid'}.'&dname='.$domainName;
  }
  my $req = new HTTP::Request GET => $childomainurl;
  $req->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
  my $res = $ua->request($req);
  if ( $res->code() eq 200 ) {
    my $decoderesp_json = decode_json($res->content);
    my $req1 = new HTTP::Request GET => $childOrgurl;
    $req1->header('Authorization' => 'Zoho-oauthtoken '.$access_token);
    my $res1 = $ua->request($req1);
    my $decodedresponseCU = decode_json($res1->content);
    if ($res1->code() eq 200) {
       print '<head><link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
             <body>
             <div class="zmcMsg zmConSucMsg">
             <i class="zm_tickIco"></i>
             <span style="color:black; font-size:16px;">
             <b>Domain Name - </b>'.$domainName.'<br>
             <b>Plan - </b>'.$decodedresponseCU->{'data'}->{'basePlan'}.'<br>
             <b>No. of License(s) - </b>'.$decodedresponseCU->{'data'}->{'licenseCount'}.'<br>
             <b>CNAME - </b>Zbcode : '.$decoderesp_json->{'data'}->{'CNAMEVerificationCode'}.'  <a href="https://www.zoho'.$region.'/mail/help/adminconsole/domain-verification.html#alink4" class="zm_link" target="_blank">Learn More</a><br>
             <a class="zm_link" href='.$encUrl.' target=_blank>Control Panel</a>
             </span>
          </div>';
          } else {
            print '<head><link href="assets/style.css" rel="stylesheet" type="text/css"> </head>
             <body>
             <div class="zmcMsg zmcErrMsg">
             <i class="zm_tickIco"></i>
             <span style="font-size:16px;">
             <b>Response -'.$res1->content.'</b><br>
             </span>
             </div>';

          }
    } else {
    print '<head><link href="style.css" rel="stylesheet" type="text/css"> </head>
             <body>
             <div class="zmcMsg zmcErrMsg">
             <i class="zm_tickIco"></i>
             <span style="font-size:16px;">
             <b>Response -'.$res->content.'</b><br>
             </span>
             </div>';
    }
}
Whostmgr::HTMLInterface::deffooter('','','','');
1;
#--------------------------------------------------------------------------------------------------------------------------------------------------------------